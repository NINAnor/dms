import uuid
from unittest.mock import patch

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
class TestDatasetValidateStorage:
    """Test cases for Dataset._validate_storage."""

    def test_validate_storage_allowed(self, dataset_with_project, project):
        """A storage present in the project's available_storages is accepted."""
        storage = _make_storage(name="assigned")
        ProjectStorage.objects.create(project=project, storage=storage)

        dataset_with_project._validate_storage(storage)  # should not raise

    def test_validate_storage_allowed_global_storage(
        self, dataset_with_project, project
    ):
        """A global storage, even without an explicit assignment, is accepted."""
        storage = _make_storage(name="global", is_global=True)

        dataset_with_project._validate_storage(storage)  # should not raise

    def test_validate_storage_rejected(self, dataset_with_project):
        """A storage not available to the project's project is rejected."""
        storage = _make_storage(name="unassigned")

        with pytest.raises(ValidationError):
            dataset_with_project._validate_storage(storage)

    def test_validate_storage_rejected_without_project(self, dataset):
        """A dataset with no project has no available storages at all."""
        storage = _make_storage(name="any")

        with pytest.raises(ValidationError):
            dataset._validate_storage(storage)


@pytest.mark.django_db(transaction=True)
class TestDatasetConfirmUpload:
    """Test cases for Dataset.confirm_upload."""

    def test_confirm_upload_creates_resource_when_object_exists(
        self, dataset_with_project, project
    ):
        storage = _make_storage(name="assigned")
        ProjectStorage.objects.create(project=project, storage=storage)
        with (
            patch.object(
                storage, "head_object", return_value={"ContentLength": 1}
            ) as mocked_head,
            patch.object(
                storage, "get_http_url", return_value="https://example.com/data.csv"
            ),
        ):
            resource = dataset_with_project.confirm_upload(storage, "data.csv")

        assert resource.pk is not None
        assert resource.storage == storage
        assert resource.key == "data.csv"
        assert resource.title == "data.csv"
        assert resource.uri == "https://example.com/data.csv"
        assert resource.dataset == dataset_with_project
        mocked_head.assert_called_once_with("data.csv")

    def test_confirm_upload_derives_title_from_key_basename(
        self, dataset_with_project, project
    ):
        storage = _make_storage(name="assigned")
        ProjectStorage.objects.create(project=project, storage=storage)
        with (
            patch.object(storage, "head_object", return_value={"ContentLength": 1}),
            patch.object(
                storage, "get_http_url", return_value="https://example.com/data.csv"
            ),
        ):
            resource = dataset_with_project.confirm_upload(
                storage, "some/prefix/data.csv"
            )

        assert resource.title == "data.csv"

    def test_confirm_upload_twice_updates_existing_resource(
        self, dataset_with_project, project
    ):
        storage = _make_storage(name="assigned")
        ProjectStorage.objects.create(project=project, storage=storage)
        with (
            patch.object(storage, "head_object", return_value={"ContentLength": 1}),
            patch.object(
                storage, "get_http_url", return_value="https://example.com/data.csv"
            ),
        ):
            first = dataset_with_project.confirm_upload(storage, "data.csv")

        with (
            patch.object(storage, "head_object", return_value={"ContentLength": 2}),
            patch.object(
                storage, "get_http_url", return_value="https://example.com/data-v2.csv"
            ),
        ):
            second = dataset_with_project.confirm_upload(storage, "data.csv")

        assert str(second.pk) == str(first.pk)
        assert second.uri == "https://example.com/data-v2.csv"
        assert dataset_with_project.resources.filter(key="data.csv").count() == 1

    def test_confirm_upload_stores_and_matches_on_resolved_s3_key(
        self, dataset_with_project, project
    ):
        storage = _make_storage(name="assigned", prefix="{dataset_id}")
        ProjectStorage.objects.create(project=project, storage=storage)
        expected_key = f"{dataset_with_project.pk}/data.csv"

        with (
            patch.object(storage, "head_object", return_value={"ContentLength": 1}),
            patch.object(
                storage, "get_http_url", return_value="https://example.com/data.csv"
            ),
        ):
            first = dataset_with_project.confirm_upload(
                storage, "data.csv", dataset_id=dataset_with_project.pk
            )

        assert first.key == expected_key

        with (
            patch.object(storage, "head_object", return_value={"ContentLength": 2}),
            patch.object(
                storage, "get_http_url", return_value="https://example.com/data-v2.csv"
            ),
        ):
            second = dataset_with_project.confirm_upload(
                storage, "data.csv", dataset_id=dataset_with_project.pk
            )

        assert str(second.pk) == str(first.pk)
        assert dataset_with_project.resources.filter(key=expected_key).count() == 1

    def test_confirm_upload_rejects_missing_object(self, dataset_with_project, project):
        storage = _make_storage(name="assigned")
        ProjectStorage.objects.create(project=project, storage=storage)
        with (
            patch.object(storage, "head_object", return_value=None),
            pytest.raises(ValidationError),
        ):
            dataset_with_project.confirm_upload(storage, "data.csv")

        assert not dataset_with_project.resources.filter(key="data.csv").exists()

    def test_confirm_upload_rejected_storage(self, dataset_with_project):
        storage = _make_storage(name="unassigned")

        with pytest.raises(ValidationError):
            dataset_with_project.confirm_upload(storage, "data.csv")


@pytest.mark.django_db(transaction=True)
class TestResourceMoveToStorage:
    """Test cases for Resource.move_to_storage."""

    def test_move_to_storage_rejects_same_storage(self, dataset_with_project, project):
        storage = _make_storage(name="assigned")
        ProjectStorage.objects.create(project=project, storage=storage)
        with (
            patch.object(storage, "head_object", return_value={"ContentLength": 1}),
            patch.object(
                storage, "get_http_url", return_value="https://example.com/data.csv"
            ),
        ):
            resource = dataset_with_project.confirm_upload(storage, "data.csv")

        with pytest.raises(ValidationError) as exc_info:
            resource.move_to_storage(storage)

        assert "same as current storage" in str(exc_info.value)

    def test_move_to_storage_rejects_unallowed_storage(
        self, dataset_with_project, project
    ):
        storage1 = _make_storage(name="assigned")
        ProjectStorage.objects.create(project=project, storage=storage1)
        storage2 = _make_storage(name="unassigned")

        with (
            patch.object(storage1, "head_object", return_value={"ContentLength": 1}),
            patch.object(
                storage1, "get_http_url", return_value="https://example.com/data.csv"
            ),
        ):
            resource = dataset_with_project.confirm_upload(storage1, "data.csv")

        with pytest.raises(ValidationError) as exc_info:
            resource.move_to_storage(storage2)

        assert "not available" in str(exc_info.value)

    def test_move_to_storage_enqueues_background_task(
        self, dataset_with_project, project
    ):
        storage1 = _make_storage(name="assigned1")
        storage2 = _make_storage(name="assigned2")
        ProjectStorage.objects.create(project=project, storage=storage1)
        ProjectStorage.objects.create(project=project, storage=storage2)

        with (
            patch.object(storage1, "head_object", return_value={"ContentLength": 1}),
            patch.object(
                storage1, "get_http_url", return_value="https://example.com/data.csv"
            ),
        ):
            resource = dataset_with_project.confirm_upload(storage1, "data.csv")

        with patch("dms.datasets.models.app.configure_task") as mock_task:
            mock_defer = mock_task.return_value.defer
            resource.move_to_storage(storage2)

            mock_task.assert_called_once_with(
                name="dms.datasets.tasks.move_resource_to_storage_task"
            )
            mock_defer.assert_called_once_with(
                resource_id=resource.pk, target_storage_id=storage2.id
            )

    def test_move_to_storage_rejects_resource_without_storage_or_key(
        self, dataset_with_project, project
    ):
        """Resource without storage or key cannot be moved."""
        storage = _make_storage(name="assigned")
        ProjectStorage.objects.create(project=project, storage=storage)

        resource = dataset_with_project.resources.create(
            id=uuid.uuid4(),
            title="External",
            uri="https://example.com/external.csv",
            # storage and key are None
        )

        with pytest.raises(ValidationError) as exc_info:
            resource.move_to_storage(storage)

        assert "storage and key" in str(exc_info.value)


@pytest.mark.django_db(transaction=True)
class TestMoveResourceToStorageTask:
    """Test cases for the move_resource_to_storage_task background task."""

    def test_task_moves_object_and_updates_resource(
        self, dataset_with_project, project
    ):
        from dms.datasets.tasks import move_resource_to_storage_task

        storage1 = _make_storage(name="assigned1")
        storage2 = _make_storage(name="assigned2")
        ProjectStorage.objects.create(project=project, storage=storage1)
        ProjectStorage.objects.create(project=project, storage=storage2)

        with (
            patch.object(storage1, "head_object", return_value={"ContentLength": 1}),
            patch.object(
                storage1, "get_http_url", return_value="https://example.com/data.csv"
            ),
        ):
            resource = dataset_with_project.confirm_upload(storage1, "data.csv")

        with (
            patch.object(Storage, "move_object_between_storages") as mock_move_object,
            patch.object(
                Storage,
                "get_http_url",
                return_value="https://example.com/new/data.csv",
            ),
        ):
            move_resource_to_storage_task(
                resource_id=resource.pk, target_storage_id=storage2.id
            )

            mock_move_object.assert_called_once_with(
                source_key=resource.key,
                target_storage=storage2,
                target_key=resource.key,
            )

        resource.refresh_from_db()
        assert resource.storage_id == storage2.id
        assert resource.uri == "https://example.com/new/data.csv"
