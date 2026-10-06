import uuid

import pytest
from django.utils import timezone

from dms.datasets.api.serializers import ResourceSerializer
from dms.datasets.models import Dataset, Resource
from dms.datasets.tests.test_models import _make_storage
from dms.projects.models import Project


@pytest.fixture
def project():
    return Project.objects.create(
        number="DS002",
        name="Serializer Test Project",
        start_date=timezone.now(),
    )


@pytest.fixture
def dataset(project):
    return Dataset.objects.create(title="Serializer Dataset", project=project)


@pytest.mark.django_db(transaction=True)
class TestResourceSerializerUriReadOnlyForDirectUpload:
    """A direct-upload resource's uri is derived server-side and must stay
    read-only once storage/key are set."""

    def test_uri_cannot_be_changed_for_direct_upload_resource(self, dataset):
        storage = _make_storage()
        resource = Resource.objects.create(
            id=uuid.uuid4(),
            uri="https://example.com/original",
            dataset=dataset,
            storage=storage,
            key="some/key.txt",
        )

        serializer = ResourceSerializer(
            instance=resource,
            data={"uri": "https://example.com/changed"},
            partial=True,
        )

        assert not serializer.is_valid()
        assert "uri" in serializer.errors

    def test_uri_can_be_resubmitted_unchanged_for_direct_upload_resource(self, dataset):
        storage = _make_storage()
        resource = Resource.objects.create(
            id=uuid.uuid4(),
            uri="https://example.com/original",
            dataset=dataset,
            storage=storage,
            key="some/key.txt",
        )

        serializer = ResourceSerializer(
            instance=resource,
            data={"uri": "https://example.com/original"},
            partial=True,
        )

        assert serializer.is_valid(), serializer.errors

    def test_uri_can_be_changed_for_non_direct_upload_resource(self, dataset):
        resource = Resource.objects.create(
            id=uuid.uuid4(),
            uri="not-a-url",
            dataset=dataset,
        )

        serializer = ResourceSerializer(
            instance=resource,
            data={"uri": "https://example.com/new"},
            partial=True,
        )

        assert serializer.is_valid(), serializer.errors

    def test_uri_can_be_set_on_create(self, dataset):
        serializer = ResourceSerializer(
            data={
                "id": str(uuid.uuid4()),
                "uri": "https://example.com/new",
                "dataset_id": str(dataset.pk),
            },
        )

        assert serializer.is_valid(), serializer.errors
