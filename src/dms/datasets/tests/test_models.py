import uuid

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone

from buckets.models import Storage
from dms.datasets.models import (
    ContributionType,
    Dataset,
    DatasetContribution,
    MapResource,
    PartitionedResource,
    RasterResource,
    Resource,
    TabularResource,
)
from dms.projects.models import Project, ProjectStorage

User = get_user_model()


@pytest.fixture
def user():
    """Create a test user."""
    return User.objects.create_user(
        username="testuser",
        email="testuser@example.com",
        password="test_user_password",  # acceptable for tests  # noqa: S106
    )


@pytest.fixture
def dataset(user):
    """Create a test dataset with tags and contributors."""
    dataset = Dataset.objects.create(title="Test Dataset", version="1.0")
    dataset.save()  # Ensure the dataset is saved

    # Add tags
    dataset.tags.add("test", "sample")

    # Add contributor
    DatasetContribution.objects.create(
        dataset=dataset, user=user, roles=[ContributionType.DATA_MANAGER]
    )

    # Refresh from database to ensure all fields are properly set
    dataset.refresh_from_db()
    return dataset


@pytest.fixture
def resource(dataset):
    """Create a test resource"""
    resource = Resource.objects.create(id=uuid.uuid4(), uri="test", dataset=dataset)
    resource.refresh_from_db()
    return resource


@pytest.mark.django_db(transaction=True)
def test_dataset_clone(dataset):
    """Test that dataset cloning works correctly, even with multiple clones."""
    # First clone
    cloned1 = dataset.clone()

    # Check that we got a new instance
    assert dataset.id != cloned1.id
    assert dataset.pk != cloned1.pk

    # Check that basic fields were copied
    assert dataset.title == cloned1.title
    assert dataset.version == cloned1.version

    # Check that tags were copied
    assert set(dataset.tags.names()) == set(cloned1.tags.names())

    # Check that contributors were copied
    original_contribution = dataset.contributor_roles.first()
    cloned1_contribution = cloned1.contributor_roles.first()

    assert original_contribution.user == cloned1_contribution.user
    assert original_contribution.roles == cloned1_contribution.roles

    # Verify we have two objects in the database
    assert Dataset.objects.count() == 2

    # Second clone from the original
    cloned2 = dataset.clone()

    # Check it's different from both original and first clone
    assert dataset.id != cloned2.id
    assert cloned1.id != cloned2.id

    # Check that basic fields were copied
    assert dataset.title == cloned2.title
    assert dataset.version == cloned2.version

    # Check that tags were copied
    assert set(dataset.tags.names()) == set(cloned2.tags.names())

    # Check that contributors were copied
    cloned2_contribution = cloned2.contributor_roles.first()
    assert original_contribution.user == cloned2_contribution.user
    assert original_contribution.roles == cloned2_contribution.roles

    # Verify we have three objects in the database
    assert Dataset.objects.count() == 3

    # Clone from a clone
    cloned3 = cloned1.clone()

    # Check it's different from all other datasets
    assert dataset.id != cloned3.id
    assert cloned1.id != cloned3.id
    assert cloned2.id != cloned3.id

    # Check that basic fields were copied
    assert cloned1.title == cloned3.title
    assert cloned1.version == cloned3.version

    # Check that tags were copied
    assert set(cloned1.tags.names()) == set(cloned3.tags.names())

    # Check that contributors were copied
    cloned3_contribution = cloned3.contributor_roles.first()
    assert cloned1_contribution.user == cloned3_contribution.user
    assert cloned1_contribution.roles == cloned3_contribution.roles

    # Verify we have four objects in the database
    assert Dataset.objects.count() == 4

    # Verify all IDs are unique
    all_ids = [dataset.id, cloned1.id, cloned2.id, cloned3.id]
    assert len(set(all_ids)) == 4  # All IDs should be unique


@pytest.mark.django_db(transaction=True)
def test_resource_convert(resource):
    # cannot convert to same type - nothing happens
    resource.to_class(Resource)

    with pytest.raises(TypeError):
        # cannot convert to non Resource types
        resource.to_class(Dataset)

    # convert to map resources
    resource.to_class(MapResource)
    assert MapResource.objects.count() == 1

    # convert back to resource
    MapResource.objects.get().to_class(Resource)
    assert MapResource.objects.count() == 0
    assert Resource.objects.get()

    # convert to table resources
    Resource.objects.get().to_class(TabularResource)
    assert TabularResource.objects.count() == 1
    # convert back to resource
    TabularResource.objects.get().to_class(Resource)
    assert TabularResource.objects.count() == 0
    assert Resource.objects.get()

    # convert to raster resources
    Resource.objects.get().to_class(RasterResource)
    assert RasterResource.objects.count() == 1
    # convert back to resource
    RasterResource.objects.get().to_class(Resource)
    assert RasterResource.objects.count() == 0
    assert Resource.objects.get()

    # cross convertions
    Resource.objects.get().to_class(MapResource)
    MapResource.objects.get().to_class(TabularResource)
    TabularResource.objects.get().to_class(RasterResource)
    RasterResource.objects.get().to_class(MapResource)


def _make_storage(**kwargs):
    defaults = {
        "name": "test-storage",
        "endpoint_url": "",
        "region": "",
        "bucket_name": "bucket",
        "access_key_id": "key",
        "secret_access_key": "secret",  # noqa: S106
        "prefix": "",
        "is_global": False,
    }
    defaults.update(kwargs)
    return Storage.objects.create(**defaults)


@pytest.fixture
def project():
    """Create a test project."""
    return Project.objects.create(
        number="DS001",
        name="Dataset Storage Project",
        start_date=timezone.now(),
    )


@pytest.fixture
def dataset_with_project(project):
    """Create a test dataset attached to a project."""
    return Dataset.objects.create(title="Project Dataset", project=project)


@pytest.mark.django_db(transaction=True)
class TestResourceStorageFields:
    """Test cases for the Resource.storage and Resource.key fields."""

    def test_storage_and_key_default_to_none(self, resource):
        """A resource created without storage/key leaves both unset."""
        assert resource.storage is None
        assert resource.key is None

    def test_uri_is_independent_of_storage(self, dataset):
        """uri stays free-text and is unrelated to storage/key."""
        storage = _make_storage()
        resource = Resource.objects.create(
            id=uuid.uuid4(),
            uri="https://example.com/some/free/text/uri",
            dataset=dataset,
            storage=storage,
            key="some/key.txt",
        )
        resource.refresh_from_db()

        assert resource.uri == "https://example.com/some/free/text/uri"
        assert resource.storage == storage
        assert resource.key == "some/key.txt"

    def test_resource_without_storage_can_still_set_uri(self, dataset):
        """Resources with no storage/key keep working with a plain uri."""
        resource = Resource.objects.create(
            id=uuid.uuid4(), uri="not-a-url", dataset=dataset
        )
        resource.refresh_from_db()

        assert resource.uri == "not-a-url"
        assert resource.storage is None
        assert resource.key is None

    def test_partitioned_resource_unaffected_by_storage_key(self, dataset):
        """PartitionedResource inherits storage/key but keeps its own fields."""
        storage = _make_storage()
        partitioned = PartitionedResource.objects.create(
            id=uuid.uuid4(),
            uri="test",
            dataset=dataset,
            storage=storage,
            key="partitioned/key",
            endpoint="https://endpoint.example.com",
            https=True,
            path_style="path",
        )
        partitioned.refresh_from_db()

        assert partitioned.storage == storage
        assert partitioned.key == "partitioned/key"
        assert partitioned.endpoint == "https://endpoint.example.com"
        assert partitioned.https is True
        assert partitioned.path_style == "path"


@pytest.mark.django_db(transaction=True)
class TestDatasetUploadResource:
    """Test cases for Dataset.upload_resource."""

    def test_upload_resource_allowed_storage(self, dataset_with_project, project):
        """A storage present in the project's available_storages is accepted."""
        storage = _make_storage(name="assigned")
        ProjectStorage.objects.create(project=project, storage=storage)

        result = dataset_with_project.upload_resource(storage, "data.csv")

        assert result["key"] == "data.csv"
        assert "upload_url" in result

    def test_upload_resource_allowed_global_storage(
        self, dataset_with_project, project
    ):
        """A global storage, even without an explicit assignment, is accepted."""
        storage = _make_storage(name="global", is_global=True)

        result = dataset_with_project.upload_resource(storage, "data.csv")

        assert result["key"] == "data.csv"
        assert "upload_url" in result

    def test_upload_resource_rejected_storage(self, dataset_with_project):
        """A storage not available to the project's project is rejected."""
        storage = _make_storage(name="unassigned")

        with pytest.raises(ValidationError):
            dataset_with_project.upload_resource(storage, "data.csv")

    def test_upload_resource_rejected_without_project(self, dataset):
        """A dataset with no project has no available storages at all."""
        storage = _make_storage(name="any")

        with pytest.raises(ValidationError):
            dataset.upload_resource(storage, "data.csv")
