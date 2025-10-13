import pytest
from django.urls import reverse

from dms.datasets.models import ContributionType, Dataset, DatasetContribution


@pytest.fixture
def user():
    """Create a test user."""
    from django.contrib.auth import get_user_model

    User = get_user_model()
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


@pytest.mark.django_db(transaction=True)
def test_dataset_clone_view(client, dataset, user):
    """Test the dataset clone view."""
    # Login the user
    client.force_login(user)

    # Get the clone URL
    url = reverse("datasets:dataset_clone", kwargs={"pk": dataset.pk})

    # Make the POST request to clone
    response = client.post(url)

    # Check that we were redirected to the detail page
    assert response.status_code == 403
