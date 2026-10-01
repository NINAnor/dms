"""Django management command to backfill Resource.storage and Resource.key fields.

This command processes Resources with media URIs (those starting with MEDIA_URL),
deriving the key by stripping the MEDIA_URL prefix and assigning them to a
specified Storage row.
"""

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from buckets.models import Storage
from dms.datasets.models import Resource


class Command(BaseCommand):
    """Backfill Resource.storage and Resource.key from MEDIA_URL-prefixed URIs."""

    help = "Backfill Resource.storage and Resource.key for media resources"

    def add_arguments(self, parser):
        parser.add_argument(
            "--storage-id",
            type=int,
            required=True,
            help="Primary key of the buckets.Storage row to assign",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Report what would be changed without writing to the database",
        )

    def handle(self, *args, **options):
        """Process and backfill Resource records."""
        storage_id = options["storage_id"]
        dry_run = options["dry_run"]

        # Validate storage exists
        try:
            storage = Storage.objects.get(pk=storage_id)
        except Storage.DoesNotExist as err:
            raise CommandError(
                f"Storage with pk={storage_id} does not exist. "
                "Please provide a valid --storage-id."
            ) from err

        # Get MEDIA_URL from settings
        media_url = settings.MEDIA_URL
        self.stdout.write(
            f"Using MEDIA_URL: {media_url!r} and Storage: {storage.name} "
            f"(pk={storage.pk})"
        )

        # Query resources to backfill
        # Condition: uri starts with MEDIA_URL AND storage is NULL
        resources_to_backfill = Resource.objects.filter(
            uri__startswith=media_url, storage__isnull=True
        )

        # Resources with non-MEDIA_URL URIs (already have storage or external URIs)
        resources_with_existing_storage = Resource.objects.filter(storage__isnull=False)
        resources_with_external_uri = Resource.objects.exclude(
            uri__startswith=media_url
        )

        # Track statistics
        updated_count = 0
        skipped_existing_storage = resources_with_existing_storage.count()
        skipped_external_uri = resources_with_external_uri.count()

        self.stdout.write(
            f"Found {resources_to_backfill.count()} resources to backfill"
        )
        self.stdout.write(
            f"Found {skipped_existing_storage} resources with existing storage "
            "(will skip)"
        )
        self.stdout.write(
            f"Found {skipped_external_uri} resources with external URIs (will skip)"
        )

        # Process each resource
        updates = []
        for resource in resources_to_backfill:
            # Derive key by stripping MEDIA_URL prefix
            key = resource.uri[len(media_url) :]

            self.stdout.write(
                f"  Resource {resource.pk}: uri={resource.uri!r} -> key={key!r}"
            )

            if not dry_run:
                resource.storage = storage
                resource.key = key
                resource.save(update_fields=["storage", "key"])
                updated_count += 1
            else:
                updated_count += 1
                updates.append((resource.pk, key))

        # Print summary
        self.stdout.write("")
        self.stdout.write("=" * 70)
        self.stdout.write("BACKFILL SUMMARY")
        self.stdout.write("=" * 70)
        self.stdout.write(f"Resources updated (or to update): {updated_count}")
        self.stdout.write(
            f"Resources skipped (already have storage): {skipped_existing_storage}"
        )
        self.stdout.write(f"Resources skipped (external URIs): {skipped_external_uri}")
        if dry_run:
            self.stdout.write("")
            self.stdout.write(self.style.WARNING("DRY RUN: No changes were written"))
        else:
            self.stdout.write("")
            self.stdout.write(
                self.style.SUCCESS(f"Successfully backfilled {updated_count} resources")
            )
