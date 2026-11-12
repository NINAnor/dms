"""Tests for django-tasks task definitions in dms.datasets.tasks."""

import uuid
from unittest.mock import patch

import pytest

from dms.datasets.models import Dataset, Resource
from dms.datasets.tasks import infer_metadata_task, update_metadata


@pytest.fixture
def dataset():
    """Create a test dataset."""
    return Dataset.objects.create(title="Test Dataset", version="1.0")


@pytest.fixture
def resource(dataset):
    """Create a test resource with deferred metadata inference disabled."""
    resource = Resource.objects.create(
        id=uuid.uuid4(),
        uri="https://example.com/resource",
        dataset=dataset,
        is_metadata_manual=True,
    )
    resource.refresh_from_db()
    return resource


@pytest.mark.django_db
def test_infer_metadata_task_calls_infer_metadata(resource):
    """The task should look up the resource and trigger synchronous inference."""
    with (
        patch("dms.datasets.tasks.close_old_connections"),
        patch.object(Resource, "infer_metadata") as mocked_infer_metadata,
    ):
        infer_metadata_task.call(resource_id=resource.pk)

    mocked_infer_metadata.assert_called_once_with(deferred=False)


@pytest.mark.django_db
def test_update_metadata_processes_non_manual_resources(dataset):
    """The periodic task should trigger inference for all non-manual resources."""
    Resource.objects.create(
        id=uuid.uuid4(),
        uri="https://example.com/manual",
        dataset=dataset,
        is_metadata_manual=True,
    )
    Resource.objects.create(
        id=uuid.uuid4(),
        uri="https://example.com/auto",
        dataset=dataset,
        is_metadata_manual=False,
    )

    with (
        patch("dms.datasets.tasks.close_old_connections"),
        patch.object(Resource, "infer_metadata") as mocked_infer_metadata,
    ):
        update_metadata.call(timestamp=0)

    mocked_infer_metadata.assert_called_once_with(deferred=False)
