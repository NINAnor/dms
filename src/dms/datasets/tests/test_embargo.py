from datetime import date, timedelta

import pytest
from django.utils import timezone
from rest_framework.test import APIRequestFactory

from dms.datasets.api.serializers import ResourceListSerializer, ResourceSerializer
from dms.datasets.models import Dataset, TabularResource
from dms.projects.models import Project


@pytest.fixture
def project():
    """Create a test project."""

    return Project.objects.create(
        number="TEST-001",
        name="Test Project",
        start_date=timezone.now(),
    )


@pytest.fixture
def dataset_no_embargo(project):
    """Create a dataset without embargo."""
    return Dataset.objects.create(
        title="Test Dataset - No Embargo",
        version="1.0",
        project=project,
    )


@pytest.fixture
def dataset_with_embargo(project):
    """Create a dataset with active embargo."""
    return Dataset.objects.create(
        title="Test Dataset - With Embargo",
        version="1.0",
        project=project,
        embargo_end_date=date.today() + timedelta(days=30),
    )


@pytest.fixture
def dataset_embargo_expired(project):
    """Create a dataset with expired embargo."""
    return Dataset.objects.create(
        title="Test Dataset - Expired Embargo",
        version="1.0",
        project=project,
        embargo_end_date=date.today() - timedelta(days=1),
    )


@pytest.fixture
def resource_no_embargo(dataset_no_embargo):
    """Create a resource in a dataset without embargo."""
    return TabularResource.objects.create(
        id="res-no-embargo",
        title="Test Resource - No Embargo",
        uri="https://example.com/data.parquet",
        dataset=dataset_no_embargo,
    )


@pytest.fixture
def resource_with_embargo(dataset_with_embargo):
    """Create a resource in a dataset with active embargo."""
    return TabularResource.objects.create(
        id="res-with-embargo",
        title="Test Resource - With Embargo",
        uri="https://example.com/data.parquet",
        dataset=dataset_with_embargo,
    )


@pytest.fixture
def resource_embargo_expired(dataset_embargo_expired):
    """Create a resource in a dataset with expired embargo."""
    return TabularResource.objects.create(
        id="res-embargo-expired",
        title="Test Resource - Expired Embargo",
        uri="https://example.com/data.parquet",
        dataset=dataset_embargo_expired,
    )


@pytest.mark.django_db
class TestEmbargoUriHiding:
    """Test that URIs are properly hidden for embargoed resources."""

    def test_resource_list_serializer_shows_uri_without_embargo(
        self, resource_no_embargo
    ):
        """ResourceListSerializer should show URI when dataset has no embargo."""
        factory = APIRequestFactory()
        request = factory.get("/")
        serializer = ResourceListSerializer(
            resource_no_embargo, context={"request": request}
        )
        assert serializer.data["uri"] == "https://example.com/data.parquet"

    def test_resource_list_serializer_hides_uri_with_embargo(
        self, resource_with_embargo
    ):
        """ResourceListSerializer should hide URI when dataset is under embargo."""
        factory = APIRequestFactory()
        request = factory.get("/")
        serializer = ResourceListSerializer(
            resource_with_embargo, context={"request": request}
        )
        assert serializer.data["uri"] is None

    def test_resource_list_serializer_shows_uri_with_expired_embargo(
        self, resource_embargo_expired
    ):
        """ResourceListSerializer should show URI when embargo has expired."""
        factory = APIRequestFactory()
        request = factory.get("/")
        serializer = ResourceListSerializer(
            resource_embargo_expired, context={"request": request}
        )
        assert serializer.data["uri"] == "https://example.com/data.parquet"

    def test_resource_serializer_shows_uri_without_embargo(self, resource_no_embargo):
        """ResourceSerializer should show URI when dataset has no embargo."""
        factory = APIRequestFactory()
        request = factory.get("/")
        serializer = ResourceSerializer(
            resource_no_embargo, context={"request": request}
        )
        assert serializer.data["uri"] == "https://example.com/data.parquet"

    def test_resource_serializer_hides_uri_with_embargo(self, resource_with_embargo):
        """ResourceSerializer should hide URI when dataset is under embargo."""
        factory = APIRequestFactory()
        request = factory.get("/")
        serializer = ResourceSerializer(
            resource_with_embargo, context={"request": request}
        )
        assert serializer.data["uri"] is None
