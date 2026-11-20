import uuid
from unittest.mock import MagicMock, patch

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


class TestSignS3RequestView:
    def test_requires_authentication(self, client, dataset, storage):
        url = reverse("api_v1:datasets-sign-s3-request", kwargs={"pk": dataset.pk})
        response = client.post(
            url,
            {"storage": storage.pk, "key": "data.csv", "method": "PUT"},
            content_type="application/json",
        )
        assert response.status_code in (401, 403)

    def test_requires_project_membership(self, client, user, dataset, storage):
        client.force_login(user)
        url = reverse("api_v1:datasets-sign-s3-request", kwargs={"pk": dataset.pk})
        response = client.post(
            url,
            {"storage": storage.pk, "key": "data.csv", "method": "PUT"},
            content_type="application/json",
        )
        assert response.status_code == 403

    def test_put_without_upload_id_signs_simple_upload(
        self, client, user, member, dataset, storage
    ):
        client.force_login(user)
        url = reverse("api_v1:datasets-sign-s3-request", kwargs={"pk": dataset.pk})
        mock_client = MagicMock()
        mock_client.generate_presigned_url.return_value = "https://example.com/put"
        with patch.object(Storage, "_client", return_value=mock_client):
            response = client.post(
                url,
                {"storage": storage.pk, "key": "data.csv", "method": "PUT"},
                content_type="application/json",
            )
        assert response.status_code == 200
        assert response.json() == {
            "url": "https://example.com/put",
            "headers": {"x-amz-acl": "private"},
            "key": "data.csv",
        }
        mock_client.generate_presigned_url.assert_called_once_with(
            "put_object",
            Params={"Bucket": "bucket", "Key": "data.csv", "ACL": "private"},
            ExpiresIn=3600,
        )
        assert not dataset.resources.exists()

    def test_put_with_upload_id_and_part_number_signs_upload_part(
        self, client, user, member, dataset, storage
    ):
        client.force_login(user)
        url = reverse("api_v1:datasets-sign-s3-request", kwargs={"pk": dataset.pk})
        mock_client = MagicMock()
        mock_client.generate_presigned_url.return_value = "https://example.com/part"
        with patch.object(Storage, "_client", return_value=mock_client):
            response = client.post(
                url,
                {
                    "storage": storage.pk,
                    "key": "big.zip",
                    "method": "PUT",
                    "uploadId": "upload-1",
                    "partNumber": 1,
                },
                content_type="application/json",
            )
        assert response.status_code == 200
        assert response.json() == {"url": "https://example.com/part"}
        mock_client.generate_presigned_url.assert_called_once_with(
            "upload_part",
            Params={
                "Bucket": "bucket",
                "Key": "big.zip",
                "UploadId": "upload-1",
                "PartNumber": 1,
            },
            ExpiresIn=3600,
        )

    def test_post_without_upload_id_signs_create_multipart_upload(
        self, client, user, member, dataset, storage
    ):
        client.force_login(user)
        url = reverse("api_v1:datasets-sign-s3-request", kwargs={"pk": dataset.pk})
        mock_client = MagicMock()
        mock_client.generate_presigned_url.return_value = "https://example.com/create"
        with patch.object(Storage, "_client", return_value=mock_client):
            response = client.post(
                url,
                {"storage": storage.pk, "key": "big.zip", "method": "POST"},
                content_type="application/json",
            )
        assert response.status_code == 200
        assert response.json() == {
            "url": "https://example.com/create",
            "key": "big.zip",
            "headers": {"x-amz-acl": "private"},
        }
        mock_client.generate_presigned_url.assert_called_once_with(
            "create_multipart_upload",
            Params={"Bucket": "bucket", "Key": "big.zip", "ACL": "private"},
            ExpiresIn=3600,
        )

    def test_post_with_upload_id_signs_complete_multipart_upload(
        self, client, user, member, dataset, storage
    ):
        client.force_login(user)
        url = reverse("api_v1:datasets-sign-s3-request", kwargs={"pk": dataset.pk})
        mock_client = MagicMock()
        mock_client.generate_presigned_url.return_value = "https://example.com/complete"
        with patch.object(Storage, "_client", return_value=mock_client):
            response = client.post(
                url,
                {
                    "storage": storage.pk,
                    "key": "big.zip",
                    "method": "POST",
                    "uploadId": "upload-1",
                },
                content_type="application/json",
            )
        assert response.status_code == 200
        assert response.json() == {"url": "https://example.com/complete"}
        mock_client.generate_presigned_url.assert_called_once_with(
            "complete_multipart_upload",
            Params={"Bucket": "bucket", "Key": "big.zip", "UploadId": "upload-1"},
            ExpiresIn=3600,
        )

    def test_delete_with_upload_id_signs_abort_multipart_upload(
        self, client, user, member, dataset, storage
    ):
        client.force_login(user)
        url = reverse("api_v1:datasets-sign-s3-request", kwargs={"pk": dataset.pk})
        mock_client = MagicMock()
        mock_client.generate_presigned_url.return_value = "https://example.com/abort"
        with patch.object(Storage, "_client", return_value=mock_client):
            response = client.post(
                url,
                {
                    "storage": storage.pk,
                    "key": "big.zip",
                    "method": "DELETE",
                    "uploadId": "upload-1",
                },
                content_type="application/json",
            )
        assert response.status_code == 200
        assert response.json() == {"url": "https://example.com/abort"}
        mock_client.generate_presigned_url.assert_called_once_with(
            "abort_multipart_upload",
            Params={"Bucket": "bucket", "Key": "big.zip", "UploadId": "upload-1"},
            ExpiresIn=3600,
        )

    def test_get_with_upload_id_signs_list_parts(
        self, client, user, member, dataset, storage
    ):
        client.force_login(user)
        url = reverse("api_v1:datasets-sign-s3-request", kwargs={"pk": dataset.pk})
        mock_client = MagicMock()
        mock_client.generate_presigned_url.return_value = (
            "https://example.com/list-parts"
        )
        with patch.object(Storage, "_client", return_value=mock_client):
            response = client.post(
                url,
                {
                    "storage": storage.pk,
                    "key": "big.zip",
                    "method": "GET",
                    "uploadId": "upload-1",
                },
                content_type="application/json",
            )
        assert response.status_code == 200
        assert response.json() == {"url": "https://example.com/list-parts"}
        mock_client.generate_presigned_url.assert_called_once_with(
            "list_parts",
            Params={"Bucket": "bucket", "Key": "big.zip", "UploadId": "upload-1"},
            ExpiresIn=3600,
        )

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
        url = reverse("api_v1:datasets-sign-s3-request", kwargs={"pk": dataset.pk})
        response = client.post(
            url,
            {"storage": other_storage.pk, "key": "data.csv", "method": "PUT"},
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_unsupported_combo_returns_400(
        self, client, user, member, dataset, storage
    ):
        """GET without an uploadId has no dispatch branch and raises
        ValueError in Storage.presign_s3_request, mapped to 400."""
        client.force_login(user)
        url = reverse("api_v1:datasets-sign-s3-request", kwargs={"pk": dataset.pk})
        response = client.post(
            url,
            {"storage": storage.pk, "key": "data.csv", "method": "GET"},
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
        url = reverse("api_v1:datasets-sign-s3-request", kwargs={"pk": dataset.pk})
        with patch.object(
            Storage, "get_s3_path", return_value="rendered/data.csv"
        ) as mocked_get_s3_path:
            response = client.post(
                url,
                {
                    "storage": storage.pk,
                    "key": "data.csv",
                    "method": "PUT",
                    # client-supplied context must be ignored
                    "project_id": "attacker-project",
                    "user_id": "999999",
                },
                content_type="application/json",
            )
        assert response.status_code == 200
        # called once by the dispatcher (to compute the resolved key) and
        # once by get_presigned_upload_url (both using the same context)
        mocked_get_s3_path.assert_called_with(
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


class TestMoveResourceToStorageView:
    def test_enqueues_background_task_and_returns_202(
        self, client, user, member, dataset, storage
    ):
        """API should enqueue background task and return 202 Accepted."""
        client.force_login(user)

        # First create a resource
        with (
            patch.object(Storage, "head_object", return_value={"ContentLength": 1}),
            patch.object(
                Storage, "get_http_url", return_value="https://example.com/data.csv"
            ),
        ):
            resource = dataset.confirm_upload(storage, "data.csv")

        # Now move it to another storage
        storage2 = Storage.objects.create(
            name="storage2",
            bucket_name="bucket2",
            access_key_id="key2",
            secret_access_key="secret2",  # noqa: S106
        )
        ProjectStorage.objects.create(project=dataset.project, storage=storage2)

        url = reverse("api_v1:resources-move-to-storage", kwargs={"pk": resource.pk})
        with patch("dms.datasets.models.app.configure_task") as mock_task:
            response = client.post(
                url,
                {"target_storage": storage2.pk},
                content_type="application/json",
            )

        assert response.status_code == 202
        mock_task.assert_called_once_with(
            name="dms.datasets.tasks.move_resource_to_storage_task"
        )
        mock_task.return_value.defer.assert_called_once()

    def test_rejects_same_storage(self, client, user, member, dataset, storage):
        """API should reject moving to same storage with 400."""
        client.force_login(user)

        # Create a resource
        with (
            patch.object(Storage, "head_object", return_value={"ContentLength": 1}),
            patch.object(
                Storage, "get_http_url", return_value="https://example.com/data.csv"
            ),
        ):
            resource = dataset.confirm_upload(storage, "data.csv")

        url = reverse("api_v1:resources-move-to-storage", kwargs={"pk": resource.pk})
        response = client.post(
            url,
            {"target_storage": storage.pk},
            content_type="application/json",
        )

        assert response.status_code == 400
        assert "same as current storage" in response.json()["errors"][0]["detail"]

    def test_rejects_disallowed_storage(self, client, user, member, dataset, storage):
        """API should reject moving to storage not in allowlist with 400."""
        client.force_login(user)

        # Create a resource
        with (
            patch.object(Storage, "head_object", return_value={"ContentLength": 1}),
            patch.object(
                Storage, "get_http_url", return_value="https://example.com/data.csv"
            ),
        ):
            resource = dataset.confirm_upload(storage, "data.csv")

        # Try to move to unallowed storage
        storage_unallowed = Storage.objects.create(
            name="unallowed",
            bucket_name="bucket_unallowed",
            access_key_id="key_unallowed",
            secret_access_key="secret_unallowed",  # noqa: S106
        )

        url = reverse("api_v1:resources-move-to-storage", kwargs={"pk": resource.pk})
        response = client.post(
            url,
            {"target_storage": storage_unallowed.pk},
            content_type="application/json",
        )

        assert response.status_code == 400
        assert "not available" in response.json()["errors"][0]["detail"]

    def test_requires_project_membership(self, client, user, dataset, storage):
        """API should require project membership (change permission)."""
        client.force_login(user)

        # Test permission requirement (no membership)
        storage2 = Storage.objects.create(
            name="storage2",
            bucket_name="bucket2",
            access_key_id="key2",
            secret_access_key="secret2",  # noqa: S106
        )

        with (
            patch.object(Storage, "head_object", return_value={"ContentLength": 1}),
            patch.object(
                Storage, "get_http_url", return_value="https://example.com/data.csv"
            ),
        ):
            resource = dataset.resources.create(
                id=uuid.uuid4(),
                title="test",
                uri="https://example.com/test.csv",
                storage=storage,
                key="test.csv",
            )

        url = reverse("api_v1:resources-move-to-storage", kwargs={"pk": resource.pk})
        response = client.post(
            url,
            {"target_storage": storage2.pk},
            content_type="application/json",
        )

        assert response.status_code == 403
