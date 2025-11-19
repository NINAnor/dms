import uuid

import pytest
from django.contrib.auth import get_user_model

from dms.datasets.models import (
    ContributionType,
    Dataset,
    DatasetContribution,
    MapResource,
    RasterResource,
    Resource,
    TabularResource,
)

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
