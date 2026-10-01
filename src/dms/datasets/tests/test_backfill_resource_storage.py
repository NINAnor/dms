"""Tests for the backfill_resource_storage management command."""

import io

import pytest
from django.conf import settings
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import override_settings

from buckets.models import Storage
from dms.datasets.models import Dataset, Resource
from dms.projects.models import Project


@pytest.fixture
def project():
    """Create a test project."""
    return Project.objects.create(
        number="TEST-001",
        name="Test Project",
        start_date="2024-01-01",
    )


@pytest.fixture
def dataset(project):
    """Create a test dataset."""
    return Dataset.objects.create(
        title="Test Dataset",
        version="1.0",
        project=project,
    )


@pytest.fixture
def storage():
    """Create a test storage."""
    return Storage.objects.create(
        name="Test Storage",
        endpoint_url="https://s3.example.com",
        region="us-east-1",
        bucket_name="test-bucket",
        access_key_id="test-key",  # noqa: S106
        secret_access_key="test-secret",  # noqa: S106
        prefix="",
        canned_acl="private",
        is_global=True,
    )


@pytest.fixture
def media_url():
    """Return the MEDIA_URL for testing."""
    return settings.MEDIA_URL


@pytest.mark.django_db
class TestBackfillResourceStorageCommand:
    """Test cases for backfill_resource_storage command."""

    def test_missing_storage_id_argument_exits_with_error(self, dataset):
        """Test that missing --storage-id argument raises CommandError."""
        out = io.StringIO()
        with pytest.raises(CommandError) as exc_info:
            call_command("backfill_resource_storage", stdout=out)
        assert "storage-id" in str(exc_info.value).lower()

    def test_invalid_storage_id_exits_with_error(self, dataset):
        """Test that invalid --storage-id raises CommandError."""
        out = io.StringIO()
        with pytest.raises(CommandError) as exc_info:
            call_command(
                "backfill_resource_storage", "--storage-id", "9999", stdout=out
            )

        assert "does not exist" in str(exc_info.value)
        assert "9999" in str(exc_info.value)

    def test_valid_storage_id_accepted(self, dataset, storage):
        """Test that valid --storage-id is accepted."""
        out = io.StringIO()
        call_command(
            "backfill_resource_storage",
            "--storage-id",
            str(storage.pk),
            "--dry-run",
            stdout=out,
        )
        output = out.getvalue()
        assert "DRY RUN: No changes were written" in output

    def test_dry_run_makes_no_db_changes(self, dataset, storage, media_url):
        """Test that --dry-run flag does not write to database."""
        # Create a resource with MEDIA_URL URI
        resource = Resource.objects.create(
            id="test-resource-1",
            title="Test Resource",
            uri=f"{media_url}test-file.txt",
            dataset=dataset,
        )

        # Verify initial state
        resource.refresh_from_db()
        assert resource.storage is None
        assert resource.key is None

        # Run with dry-run
        out = io.StringIO()
        call_command(
            "backfill_resource_storage",
            "--storage-id",
            str(storage.pk),
            "--dry-run",
            stdout=out,
        )

        # Verify no changes were made
        resource.refresh_from_db()
        assert resource.storage is None
        assert resource.key is None

        output = out.getvalue()
        assert "DRY RUN: No changes were written" in output
        assert "1" in output  # Should report 1 resource would be updated

    def test_correct_prefix_stripping_and_key_derivation(
        self, dataset, storage, media_url
    ):
        """Test that MEDIA_URL prefix is correctly stripped to derive key."""
        # Create resources with MEDIA_URL URIs
        resource1 = Resource.objects.create(
            id="test-resource-1",
            title="Test Resource 1",
            uri=f"{media_url}file1.txt",
            dataset=dataset,
        )
        resource2 = Resource.objects.create(
            id="test-resource-2",
            title="Test Resource 2",
            uri=f"{media_url}subdir/file2.txt",
            dataset=dataset,
        )

        # Run command
        out = io.StringIO()
        call_command(
            "backfill_resource_storage",
            "--storage-id",
            str(storage.pk),
            stdout=out,
        )

        # Verify resources were updated with correct keys
        resource1.refresh_from_db()
        assert resource1.storage.pk == storage.pk
        assert resource1.key == "file1.txt"

        resource2.refresh_from_db()
        assert resource2.storage.pk == storage.pk
        assert resource2.key == "subdir/file2.txt"

        output = out.getvalue()
        assert "file1.txt" in output
        assert "subdir/file2.txt" in output

    def test_skip_resources_with_non_media_url_uri(self, dataset, storage):
        """Test that resources with non-MEDIA_URL URIs are skipped."""
        # Create resource with external URI
        resource = Resource.objects.create(
            id="test-resource-1",
            title="Test Resource",
            uri="https://external.example.com/file.txt",
            dataset=dataset,
        )

        # Run command
        out = io.StringIO()
        call_command(
            "backfill_resource_storage",
            "--storage-id",
            str(storage.pk),
            stdout=out,
        )

        # Verify resource was not updated
        resource.refresh_from_db()
        assert resource.storage is None
        assert resource.key is None

        output = out.getvalue()
        assert "Resources updated" in output
        # Should report 0 updated and 1 external URI skipped
        assert "1" in output.split("external URIs")[0].split("\n")[-1]

    def test_skip_resources_that_already_have_storage(
        self, dataset, storage, media_url
    ):
        """Test that resources with existing storage are skipped."""
        # Create a separate storage for existing resource
        existing_storage = Storage.objects.create(
            name="Existing Storage",
            endpoint_url="https://s3.example.com",
            region="us-east-1",
            bucket_name="existing-bucket",
            access_key_id="existing-key",  # noqa: S106
            secret_access_key="existing-secret",  # noqa: S106
            prefix="",
            canned_acl="private",
            is_global=True,
        )

        # Create resource that already has storage
        resource = Resource.objects.create(
            id="test-resource-1",
            title="Test Resource",
            uri=f"{media_url}file.txt",
            dataset=dataset,
            storage=existing_storage,
            key="original-key.txt",
        )

        # Run command
        out = io.StringIO()
        call_command(
            "backfill_resource_storage",
            "--storage-id",
            str(storage.pk),
            stdout=out,
        )

        # Verify resource was not changed
        resource.refresh_from_db()
        assert resource.storage.pk == existing_storage.pk
        assert resource.key == "original-key.txt"

        output = out.getvalue()
        assert "Resources updated (or to update): 0" in output
        assert "1" in output.split("existing storage")[0].split("\n")[-1]

    def test_uri_field_left_unchanged_after_backfill(self, dataset, storage, media_url):
        """Test that URI field is completely untouched after backfill."""
        original_uri = f"{media_url}test-file.txt"
        resource = Resource.objects.create(
            id="test-resource-1",
            title="Test Resource",
            uri=original_uri,
            dataset=dataset,
        )

        # Run command
        out = io.StringIO()
        call_command(
            "backfill_resource_storage",
            "--storage-id",
            str(storage.pk),
            stdout=out,
        )

        # Verify URI is unchanged
        resource.refresh_from_db()
        assert resource.uri == original_uri
        assert resource.storage.pk == storage.pk
        assert resource.key == "test-file.txt"

    def test_summary_output_format(self, dataset, storage, media_url):
        """Test that summary output includes correct statistics."""
        # Create resources with mixed URIs
        Resource.objects.create(
            id="test-resource-1",
            title="Media Resource",
            uri=f"{media_url}media-file.txt",
            dataset=dataset,
        )

        Resource.objects.create(
            id="test-resource-2",
            title="External Resource",
            uri="https://external.example.com/file.txt",
            dataset=dataset,
        )

        existing_storage = Storage.objects.create(
            name="Existing Storage",
            endpoint_url="https://s3.example.com",
            region="us-east-1",
            bucket_name="existing-bucket",
            access_key_id="existing-key",  # noqa: S106
            secret_access_key="existing-secret",  # noqa: S106
            prefix="",
            canned_acl="private",
            is_global=True,
        )

        Resource.objects.create(
            id="test-resource-3",
            title="Stored Resource",
            uri=f"{media_url}stored-file.txt",
            dataset=dataset,
            storage=existing_storage,
            key="existing-key.txt",
        )

        # Run command
        out = io.StringIO()
        call_command(
            "backfill_resource_storage",
            "--storage-id",
            str(storage.pk),
            stdout=out,
        )

        output = out.getvalue()

        # Verify summary sections
        assert "BACKFILL SUMMARY" in output
        assert "Resources updated (or to update): 1" in output
        assert "Resources skipped (already have storage): 1" in output
        assert "Resources skipped (external URIs): 1" in output
        assert "Successfully backfilled 1 resources" in output

    def test_multiple_resources_backfill(self, dataset, storage, media_url):
        """Test backfilling multiple resources at once."""
        # Create multiple resources with MEDIA_URL URIs
        resource_ids = []
        for i in range(5):
            res = Resource.objects.create(
                id=f"test-resource-{i}",
                title=f"Test Resource {i}",
                uri=f"{media_url}file-{i}.txt",
                dataset=dataset,
            )
            resource_ids.append(res.id)

        # Run command
        out = io.StringIO()
        call_command(
            "backfill_resource_storage",
            "--storage-id",
            str(storage.pk),
            stdout=out,
        )

        # Verify all resources were updated
        for i, res_id in enumerate(resource_ids):
            resource = Resource.objects.get(id=res_id)
            assert resource.storage.pk == storage.pk
            assert resource.key == f"file-{i}.txt"

        output = out.getvalue()
        assert "Resources updated (or to update): 5" in output
        assert "Successfully backfilled 5 resources" in output

    def test_empty_key_derived_from_media_url_only(self, dataset, storage):
        """Test edge case where URI equals MEDIA_URL exactly."""
        # Create resource where uri == MEDIA_URL
        resource = Resource.objects.create(
            id="test-resource-1",
            title="Test Resource",
            uri=settings.MEDIA_URL,
            dataset=dataset,
        )

        # Run command
        out = io.StringIO()
        call_command(
            "backfill_resource_storage",
            "--storage-id",
            str(storage.pk),
            stdout=out,
        )

        # Verify resource was updated with empty key
        resource.refresh_from_db()
        assert resource.storage.pk == storage.pk
        assert resource.key == ""

    @override_settings(MEDIA_URL="http://media.testserver/")
    def test_with_custom_media_url_setting(self, dataset, storage):
        """Test backfill with a custom MEDIA_URL setting."""
        custom_media_url = settings.MEDIA_URL
        assert custom_media_url == "http://media.testserver/"

        # Create resource with custom MEDIA_URL
        resource = Resource.objects.create(
            id="test-resource-1",
            title="Test Resource",
            uri=f"{custom_media_url}file.txt",
            dataset=dataset,
        )

        # Run command
        out = io.StringIO()
        call_command(
            "backfill_resource_storage",
            "--storage-id",
            str(storage.pk),
            stdout=out,
        )

        # Verify resource was updated correctly
        resource.refresh_from_db()
        assert resource.storage.pk == storage.pk
        assert resource.key == "file.txt"
