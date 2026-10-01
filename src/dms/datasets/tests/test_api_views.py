from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone

from buckets.models import Storage
from dms.datasets.models import Dataset
from dms.projects.models import Project, ProjectMembership, ProjectStorage

User = get_user_model()

pytestmark = pytest.mark.django_db(transaction=True)


@pytest.fixture
def user():
    return User.objects.create_user(
        username="apiuser",
        email="apiuser@example.com",
        password="test_user_password",  # acceptable for tests  # noqa: S106
    )


@pytest.fixture
def project():
    return Project.objects.create(
        number="API001",
        name="API Test Project",
        start_date=timezone.now(),
    )


@pytest.fixture
def member(user, project):
    """Grant `user` membership (and thus 'change' permission) on `project`."""
    return ProjectMembership.objects.create(project=project, user=user)


@pytest.fixture
def dataset(project):
    return Dataset.objects.create(title="API Dataset", project=project)


@pytest.fixture
def storage(project):
    storage = Storage.objects.create(
        name="api-storage",
        endpoint_url="",
        region="",
        bucket_name="bucket",
        access_key_id="key",
        secret_access_key="secret",  # noqa: S106
        prefix="",
        is_global=False,
    )
    ProjectStorage.objects.create(project=project, storage=storage)
    return storage


class TestUploadResourceView:
    def test_requires_authentication(self, client, dataset, storage):
        url = reverse("api_v1:datasets-upload-resource", kwargs={"pk": dataset.pk})
        response = client.post(
            url,
            {"storage": storage.pk, "filename": "data.csv"},
            content_type="application/json",
        )
        assert response.status_code in (401, 403)

    def test_requires_project_membership(self, client, user, dataset, storage):
        client.force_login(user)
        url = reverse("api_v1:datasets-upload-resource", kwargs={"pk": dataset.pk})
        response = client.post(
            url,
            {"storage": storage.pk, "filename": "data.csv"},
            content_type="application/json",
        )
        assert response.status_code == 403

    def test_returns_upload_url_without_creating_resource(
        self, client, user, member, dataset, storage
    ):
        client.force_login(user)
        url = reverse("api_v1:datasets-upload-resource", kwargs={"pk": dataset.pk})
        with patch.object(
            Storage, "get_presigned_upload_url", return_value="https://example.com/put"
        ) as mocked:
            response = client.post(
                url,
                {"storage": storage.pk, "filename": "data.csv"},
                content_type="application/json",
            )
        assert response.status_code == 200
        assert response.json() == {
            "key": "data.csv",
            "upload_url": "https://example.com/put",
        }
        mocked.assert_called_once_with(
            "data.csv",
            project_id=dataset.project_id,
            dataset_id=str(dataset.id),
            user_id=user.id,
        )
        assert not dataset.resources.exists()

    def test_rejects_storage_not_available_to_project(
        self, client, user, member, dataset
    ):
        other_storage = Storage.objects.create(
            name="unassigned-storage",
            endpoint_url="",
            region="",
            bucket_name="bucket",
            access_key_id="key",
            secret_access_key="secret",  # noqa: S106
            prefix="",
            is_global=False,
        )
        client.force_login(user)
        url = reverse("api_v1:datasets-upload-resource", kwargs={"pk": dataset.pk})
        response = client.post(
            url,
            {"storage": other_storage.pk, "filename": "data.csv"},
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_prefix_context_contains_project_dataset_and_user(
        self, client, user, member, dataset, storage
    ):
        """The server-side context passed to ``Storage.get_s3_path`` (and
        thus rendered into the prefix template) must include
        project_id/dataset_id/user_id, never trusting client input for it."""
        client.force_login(user)
        url = reverse("api_v1:datasets-upload-resource", kwargs={"pk": dataset.pk})
        with patch.object(
            Storage, "get_s3_path", return_value="rendered/data.csv"
        ) as mocked_get_s3_path:
            response = client.post(
                url,
                {
                    "storage": storage.pk,
                    "filename": "data.csv",
                    # client-supplied context must be ignored
                    "project_id": "attacker-project",
                    "user_id": "999999",
                },
                content_type="application/json",
            )
        assert response.status_code == 200
        mocked_get_s3_path.assert_called_once_with(
            "data.csv",
            project_id=dataset.project_id,
            dataset_id=str(dataset.id),
            user_id=user.id,
        )


class TestAvailableStoragesView:
    def test_lists_storages_available_to_dataset_project(
        self, client, dataset, storage
    ):
        url = reverse("api_v1:datasets-available-storages", kwargs={"pk": dataset.pk})
        response = client.get(url)
        assert response.status_code == 200
        assert response.json() == [{"id": storage.pk, "name": storage.name}]

    def test_empty_for_dataset_without_project(self, client):
        dataset = Dataset.objects.create(title="No Project Dataset")
        url = reverse("api_v1:datasets-available-storages", kwargs={"pk": dataset.pk})
        response = client.get(url)
        assert response.status_code == 200
        assert response.json() == []


class TestConfirmUploadView:
    def test_creates_resource_when_object_exists_in_storage(
        self, client, user, member, dataset, storage
    ):
        client.force_login(user)
        url = reverse("api_v1:datasets-confirm-upload", kwargs={"pk": dataset.pk})
        with (
            patch.object(
                Storage, "head_object", return_value={"ContentLength": 1}
            ) as mocked_head,
            patch.object(
                Storage, "get_http_url", return_value="https://example.com/data.csv"
            ),
        ):
            response = client.post(
                url,
                {"storage": storage.pk, "key": "data.csv"},
                content_type="application/json",
            )
        assert response.status_code == 201
        mocked_head.assert_called_once_with(
            "data.csv",
            project_id=dataset.project_id,
            dataset_id=str(dataset.id),
            user_id=user.id,
        )
        resource = dataset.resources.get(key="data.csv")
        assert resource.storage == storage
        assert resource.uri == "https://example.com/data.csv"
        assert response.json()["id"] == str(resource.pk)

    def test_rejects_when_object_missing_from_storage(
        self, client, user, member, dataset, storage
    ):
        client.force_login(user)
        url = reverse("api_v1:datasets-confirm-upload", kwargs={"pk": dataset.pk})
        with patch.object(Storage, "head_object", return_value=None):
            response = client.post(
                url,
                {"storage": storage.pk, "key": "data.csv"},
                content_type="application/json",
            )
        assert response.status_code == 400
        assert not dataset.resources.filter(key="data.csv").exists()

    def test_requires_project_membership(self, client, user, dataset, storage):
        client.force_login(user)
        url = reverse("api_v1:datasets-confirm-upload", kwargs={"pk": dataset.pk})
        response = client.post(
            url,
            {"storage": storage.pk, "key": "data.csv"},
            content_type="application/json",
        )
        assert response.status_code == 403
