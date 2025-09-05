from unittest.mock import Mock

import pytest
from django.contrib.auth import get_user_model

from dms.datasets.models import Dataset, Resource
from dms.datasets.rules import dataset_in_user_projects, resource_in_user_projects
from dms.projects.models import Project, ProjectMembership

User = get_user_model()


@pytest.fixture
def setup_test_data():
    user = User.objects.create_user(email="testuser@example.com", username="testuser")
    staff_user = User.objects.create_user(
        email="staffuser@example.com", is_staff=True, username="staffuser"
    )
    other_user = User.objects.create_user(
        email="otheruser@example.com", username="otheruser"
    )
    unauthenticated_user = Mock()
    unauthenticated_user.is_authenticated = False

    project = Project.objects.create(
        number="TEST001", name="Test Project", start_date="2023-01-01T00:00:00Z"
    )

    other_project = Project.objects.create(
        number="TEST002", name="Other Test Project", start_date="2023-01-01T00:00:00Z"
    )

    # Create membership for authenticated user in first project
    ProjectMembership.objects.create(
        project=project, user=user, role=ProjectMembership.Role.MEMBER
    )

    # Create membership for other user in second project
    ProjectMembership.objects.create(
        project=other_project, user=other_user, role=ProjectMembership.Role.MEMBER
    )

    # Create datasets
    dataset_with_project = Dataset.objects.create(
        id="dataset1", title="Dataset with Project", project=project
    )

    dataset_without_project = Dataset.objects.create(
        id="dataset2", title="Dataset without Project"
    )

    dataset_other_project = Dataset.objects.create(
        id="dataset3", title="Dataset in Other Project", project=other_project
    )

    # Create resources
    resource_with_project = Resource.objects.create(
        id="resource1",
        title="Resource with Project",
        uri="http://example.com/resource1",
        dataset=dataset_with_project,
    )

    resource_without_project = Resource.objects.create(
        id="resource2",
        title="Resource without Project",
        uri="http://example.com/resource2",
        dataset=dataset_without_project,
    )

    return {
        "user": user,
        "staff_user": staff_user,
        "other_user": other_user,
        "unauthenticated_user": unauthenticated_user,
        "project": project,
        "other_project": other_project,
        "dataset_with_project": dataset_with_project,
        "dataset_without_project": dataset_without_project,
        "dataset_other_project": dataset_other_project,
        "resource_with_project": resource_with_project,
        "resource_without_project": resource_without_project,
    }


@pytest.mark.django_db(transaction=True)
def test_dataset_in_user_projects_unauthenticated(setup_test_data):
    """Test that unauthenticated users cannot access datasets"""
    data = setup_test_data
    result = dataset_in_user_projects(
        data["unauthenticated_user"], data["dataset_with_project"]
    )
    assert result is False


@pytest.mark.django_db(transaction=True)
def test_dataset_in_user_projects_none_dataset(setup_test_data):
    """Test that authenticated users can access None datasets"""
    data = setup_test_data
    result = dataset_in_user_projects(data["user"], None)
    assert result is True


@pytest.mark.django_db(transaction=True)
def test_dataset_in_user_projects_no_project_staff(setup_test_data):
    """Test that staff users can access datasets without projects"""
    data = setup_test_data
    result = dataset_in_user_projects(
        data["staff_user"], data["dataset_without_project"]
    )
    assert result is True


@pytest.mark.django_db(transaction=True)
def test_dataset_in_user_projects_no_project_non_staff(setup_test_data):
    """Test that non-staff users cannot access
    datasets without projects (project_id is None)"""
    data = setup_test_data
    result = dataset_in_user_projects(data["user"], data["dataset_without_project"])
    assert result is False


@pytest.mark.django_db(transaction=True)
def test_dataset_in_user_projects_user_in_project(setup_test_data):
    """Test that users can access datasets from projects they're members of"""
    data = setup_test_data
    result = dataset_in_user_projects(data["user"], data["dataset_with_project"])
    assert result is True


@pytest.mark.django_db(transaction=True)
def test_dataset_in_user_projects_user_not_in_project(setup_test_data):
    """Test that users cannot access datasets from projects they're not members of"""
    data = setup_test_data
    result = dataset_in_user_projects(data["user"], data["dataset_other_project"])
    assert result is False


@pytest.mark.django_db(transaction=True)
def test_resource_in_user_projects_unauthenticated(setup_test_data):
    """Test that unauthenticated users cannot access resources"""
    data = setup_test_data
    result = resource_in_user_projects(
        data["unauthenticated_user"], data["resource_with_project"]
    )
    assert result is False


@pytest.mark.django_db(transaction=True)
def test_resource_in_user_projects_none_resource(setup_test_data):
    """Test that authenticated users can access None resources"""
    data = setup_test_data
    result = resource_in_user_projects(data["user"], None)
    assert result is True


@pytest.mark.django_db(transaction=True)
def test_resource_in_user_projects_no_project(setup_test_data):
    """Test resources without projects return False"""
    data = setup_test_data
    result = resource_in_user_projects(data["user"], data["resource_without_project"])
    assert result is False


@pytest.mark.django_db(transaction=True)
def test_resource_in_user_projects_user_in_project(setup_test_data):
    """Test that users can access resources from projects they're members of"""
    data = setup_test_data
    result = resource_in_user_projects(data["user"], data["resource_with_project"])
    assert result is True


@pytest.mark.django_db(transaction=True)
def test_resource_in_user_projects_user_not_in_project(setup_test_data):
    """Test that users cannot access resources from projects they're not members of"""
    data = setup_test_data
    other_resource = Resource.objects.create(
        id="resource3",
        title="Resource in Other Project",
        uri="http://example.com/resource3",
        dataset=data["dataset_other_project"],
    )

    result = resource_in_user_projects(data["user"], other_resource)
    assert result is False
