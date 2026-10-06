from unittest.mock import MagicMock, patch

import pytest

from buckets.api.mixins import _presign_uppy_s3_request
from buckets.models import Storage


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
def storage():
    return _make_storage()


@pytest.fixture
def mock_client(storage):
    client = MagicMock()
    client.generate_presigned_url.return_value = "https://example.com/signed"
    with patch.object(storage, "_client", return_value=client):
        yield client


@pytest.mark.django_db(transaction=True)
class TestPresignS3Request:
    """Test cases for ``_presign_uppy_s3_request``'s dispatch logic."""

    def test_put_without_upload_id_signs_simple_upload(self, storage, mock_client):
        result = _presign_uppy_s3_request(storage, "data.csv", "PUT")

        assert result == {
            "url": "https://example.com/signed",
            "headers": {"x-amz-acl": "private"},
            "key": "data.csv",
        }
        mock_client.generate_presigned_url.assert_called_once_with(
            "put_object",
            Params={"Bucket": "bucket", "Key": "data.csv", "ACL": "private"},
            ExpiresIn=3600,
        )

    def test_put_with_upload_id_and_part_number_signs_upload_part(
        self, storage, mock_client
    ):
        result = _presign_uppy_s3_request(
            storage, "big.zip", "PUT", upload_id="upload-1", part_number=1
        )

        assert result == {"url": "https://example.com/signed"}
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
        self, storage, mock_client
    ):
        result = _presign_uppy_s3_request(storage, "big.zip", "POST")

        assert result == {
            "url": "https://example.com/signed",
            "key": "big.zip",
            "headers": {"x-amz-acl": "private"},
        }
        mock_client.generate_presigned_url.assert_called_once_with(
            "create_multipart_upload",
            Params={"Bucket": "bucket", "Key": "big.zip", "ACL": "private"},
            ExpiresIn=3600,
        )

    def test_post_with_upload_id_signs_complete_multipart_upload(
        self, storage, mock_client
    ):
        result = _presign_uppy_s3_request(
            storage, "big.zip", "POST", upload_id="upload-1"
        )

        assert result == {"url": "https://example.com/signed"}
        mock_client.generate_presigned_url.assert_called_once_with(
            "complete_multipart_upload",
            Params={"Bucket": "bucket", "Key": "big.zip", "UploadId": "upload-1"},
            ExpiresIn=3600,
        )

    def test_delete_with_upload_id_signs_abort_multipart_upload(
        self, storage, mock_client
    ):
        result = _presign_uppy_s3_request(
            storage, "big.zip", "DELETE", upload_id="upload-1"
        )

        assert result == {"url": "https://example.com/signed"}
        mock_client.generate_presigned_url.assert_called_once_with(
            "abort_multipart_upload",
            Params={"Bucket": "bucket", "Key": "big.zip", "UploadId": "upload-1"},
            ExpiresIn=3600,
        )

    def test_get_with_upload_id_signs_list_parts(self, storage, mock_client):
        result = _presign_uppy_s3_request(
            storage, "big.zip", "GET", upload_id="upload-1"
        )

        assert result == {"url": "https://example.com/signed"}
        mock_client.generate_presigned_url.assert_called_once_with(
            "list_parts",
            Params={"Bucket": "bucket", "Key": "big.zip", "UploadId": "upload-1"},
            ExpiresIn=3600,
        )

    def test_put_part_passes_through_expires_in(self, storage, mock_client):
        _presign_uppy_s3_request(
            storage,
            "big.zip",
            "PUT",
            upload_id="upload-1",
            part_number=2,
            expires_in=60,
        )

        mock_client.generate_presigned_url.assert_called_once_with(
            "upload_part",
            Params={
                "Bucket": "bucket",
                "Key": "big.zip",
                "UploadId": "upload-1",
                "PartNumber": 2,
            },
            ExpiresIn=60,
        )

    def test_put_without_upload_id_renders_context_into_key(self, storage, mock_client):
        storage.prefix = "{project_id}"

        result = _presign_uppy_s3_request(
            storage, "data.csv", "PUT", project_id="proj-1"
        )

        assert result["key"] == "proj-1/data.csv"

    def test_unsupported_combo_raises_value_error(self, storage):
        """GET without an uploadId has no dispatch branch."""
        with pytest.raises(ValueError, match="Unsupported presign request"):
            _presign_uppy_s3_request(storage, "data.csv", "GET")

    def test_post_with_upload_id_but_no_part_number_is_not_treated_as_part(
        self, storage, mock_client
    ):
        """PUT + upload_id but no part_number falls through to simple PutObject,
        matching the dispatch's explicit truthiness check on part_number."""
        result = _presign_uppy_s3_request(
            storage, "data.csv", "PUT", upload_id="upload-1"
        )

        assert result == {
            "url": "https://example.com/signed",
            "headers": {"x-amz-acl": "private"},
            "key": "data.csv",
        }
        mock_client.generate_presigned_url.assert_called_once_with(
            "put_object",
            Params={"Bucket": "bucket", "Key": "data.csv", "ACL": "private"},
            ExpiresIn=3600,
        )
