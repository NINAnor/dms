"""Tests for buckets.models.Storage.move_object_between_storages."""

from unittest.mock import MagicMock, patch

import pytest

from buckets.models import Storage

# noqa: S106 - hardcoded strings acceptable for tests


@pytest.fixture
def storage1():
    """Create first test storage."""
    return Storage.objects.create(
        name="storage1",
        bucket_name="bucket1",
        access_key_id="key1",
        secret_access_key="secret1",  # noqa: S106
        endpoint_url="https://s3.example.com",
    )


@pytest.fixture
def storage2():
    """Create second test storage."""
    return Storage.objects.create(
        name="storage2",
        bucket_name="bucket2",
        access_key_id="key2",
        secret_access_key="secret2",  # noqa: S106
        endpoint_url="https://s3.example.com",
    )


@pytest.mark.django_db(transaction=True)
class TestStorageMoveObjectBetweenStorages:
    """Test cases for Storage.move_object_between_storages."""

    def test_move_object_copies_object(self, storage1, storage2):
        """Object should be copied to target storage."""
        with (
            patch.object(storage1, "_client"),
            patch.object(storage2, "_client") as mock_target_client,
            patch.object(storage2, "head_object", return_value={"ContentLength": 100}),
        ):
            mock_target_s3 = MagicMock()
            mock_target_client.return_value = mock_target_s3

            storage1.move_object_between_storages(
                source_key="source.txt",
                target_storage=storage2,
                target_key="target.txt",
            )

            mock_target_s3.copy_object.assert_called_once()
            call_kwargs = mock_target_s3.copy_object.call_args[1]
            assert call_kwargs["Bucket"] == "bucket2"
            assert call_kwargs["Key"] == "target.txt"
            assert call_kwargs["CopySource"]["Bucket"] == "bucket1"
            assert call_kwargs["CopySource"]["Key"] == "source.txt"

    def test_move_object_verifies_copy(self, storage1, storage2):
        """Copy should be verified via head_object on target."""
        with (
            patch.object(storage1, "_client"),
            patch.object(storage2, "_client") as mock_target_client,
            patch.object(
                storage2, "head_object", return_value={"ContentLength": 100}
            ) as mock_head,
        ):
            mock_target_s3 = MagicMock()
            mock_target_client.return_value = mock_target_s3

            storage1.move_object_between_storages(
                source_key="source.txt",
                target_storage=storage2,
                target_key="target.txt",
            )

            # head_object should have been called to verify
            mock_head.assert_called_once_with("target.txt")

    def test_move_object_deletes_source_on_success(self, storage1, storage2):
        """Source object should be deleted after successful copy."""
        with (
            patch.object(storage1, "_client") as mock_source_client,
            patch.object(storage2, "_client") as mock_target_client,
            patch.object(storage2, "head_object", return_value={"ContentLength": 100}),
        ):
            mock_source_s3 = MagicMock()
            mock_source_client.return_value = mock_source_s3
            mock_target_s3 = MagicMock()
            mock_target_client.return_value = mock_target_s3

            storage1.move_object_between_storages(
                source_key="source.txt",
                target_storage=storage2,
                target_key="target.txt",
            )

            mock_source_s3.delete_object.assert_called_once_with(
                Bucket="bucket1", Key="source.txt"
            )

    def test_move_object_raises_on_copy_failure(self, storage1, storage2):
        """Should raise if copy fails."""
        with (
            patch.object(storage1, "_client"),
            patch.object(storage2, "_client") as mock_target_client,
        ):
            mock_target_s3 = MagicMock()
            mock_target_s3.copy_object.side_effect = Exception("Copy failed")
            mock_target_client.return_value = mock_target_s3

            with pytest.raises(Exception, match="Copy failed"):
                storage1.move_object_between_storages(
                    source_key="source.txt",
                    target_storage=storage2,
                    target_key="target.txt",
                )

    def test_move_object_raises_on_verify_failure(self, storage1, storage2):
        """Should raise if target verification fails."""
        with (
            patch.object(storage1, "_client"),
            patch.object(storage2, "_client") as mock_target_client,
            patch.object(
                storage2, "head_object", side_effect=Exception("Verify failed")
            ),
        ):
            mock_target_s3 = MagicMock()
            mock_target_client.return_value = mock_target_s3

            with pytest.raises(Exception):  # noqa: B017
                storage1.move_object_between_storages(
                    source_key="source.txt",
                    target_storage=storage2,
                    target_key="target.txt",
                )

    @patch("buckets.models.logger")
    def test_move_object_logs_but_ignores_delete_failure(
        self, mock_logger, storage1, storage2
    ):
        """Failed source deletion should be logged but not raise."""
        with (
            patch.object(storage1, "_client") as mock_source_client,
            patch.object(storage2, "_client") as mock_target_client,
            patch.object(storage2, "head_object", return_value={"ContentLength": 100}),
        ):
            mock_source_s3 = MagicMock()
            mock_source_s3.delete_object.side_effect = Exception("Delete failed")
            mock_source_client.return_value = mock_source_s3
            mock_target_s3 = MagicMock()
            mock_target_client.return_value = mock_target_s3

            # Should not raise
            storage1.move_object_between_storages(
                source_key="source.txt",
                target_storage=storage2,
                target_key="target.txt",
            )

            # Should have logged warning
            mock_logger.warning.assert_called_once()
            warning_msg = mock_logger.warning.call_args[0][0]
            assert "Failed to delete source object" in warning_msg
            assert "orphaned object" in warning_msg
