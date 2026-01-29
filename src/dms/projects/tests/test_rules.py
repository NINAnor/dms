"""Unit tests for DMP rules and permissions."""

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.utils import timezone

from dms.projects.models import DMP, DMPSchema, Project, ProjectMembership

User = get_user_model()


@pytest.fixture
def dmp_test_data():
    """Create all necessary test data for DMP rules tests."""
    # Create schema
    schema = DMPSchema.objects.create(
        name="Test Schema",
        config={},
    )

    # Create projects
    project1 = Project.objects.create(
        number="P001",
        name="Test Project",
        start_date=timezone.now(),
    )
    project2 = Project.objects.create(
        number="P002",
        name="Test Project 2",
        start_date=timezone.now(),
    )

    # Create users
    owner_user = User.objects.create_user(
        username="owner",
        email="owner@example.com",
        password="testpass123",  # noqa: S106
    )
    owner_user2 = User.objects.create_user(
        username="owner2",
        email="owner2@example.com",
        password="testpass123",  # noqa: S106
    )
    member_user = User.objects.create_user(
        username="member",
        email="member@example.com",
        password="testpass123",  # noqa: S106
    )
    member_user2 = User.objects.create_user(
        username="member2",
        email="member2@example.com",
        password="testpass123",  # noqa: S106
    )
    manager_user = User.objects.create_user(
        username="manager",
        email="manager@example.com",
        password="testpass123",  # noqa: S106
    )
    manager_user2 = User.objects.create_user(
        username="manager2",
        email="manager2@example.com",
        password="testpass123",  # noqa: S106
    )
    non_member_user = User.objects.create_user(
        username="nonmember",
        email="nonmember@example.com",
        password="testpass123",  # noqa: S106
    )
    non_member_user2 = User.objects.create_user(
        username="nonmember2",
        email="nonmember2@example.com",
        password="testpass123",  # noqa: S106
    )

    # Create DMPs
    dmp_with_project = DMP.objects.create(
        name="Test DMP",
        owner=owner_user,
        schema_from=schema,
        project=project1,
    )
    dmp_without_project = DMP.objects.create(
        name="Standalone DMP",
        owner=owner_user,
        schema_from=schema,
    )
    dmp_with_project2 = DMP.objects.create(
        name="DMP with Project 2",
        owner=owner_user2,
        schema_from=schema,
        project=project2,
    )

    return {
        "schema": schema,
        "project1": project1,
        "project2": project2,
        "owner_user": owner_user,
        "owner_user2": owner_user2,
        "member_user": member_user,
        "member_user2": member_user2,
        "manager_user": manager_user,
        "manager_user2": manager_user2,
        "non_member_user": non_member_user,
        "non_member_user2": non_member_user2,
        "dmp_with_project": dmp_with_project,
        "dmp_without_project": dmp_without_project,
        "dmp_with_project2": dmp_with_project2,
    }


@pytest.mark.django_db(transaction=True)
class TestDmpProjectRoleIs:
    """Test cases for DMP permissions based on project roles."""

    def test_owner_role_allows_project_owner(self, dmp_test_data):
        """Test that user with OWNER role in project has change permission."""
        ProjectMembership.objects.create(
            project=dmp_test_data["project1"],
            user=dmp_test_data["owner_user"],
            role=ProjectMembership.Role.OWNER,
        )
        assert dmp_test_data["owner_user"].has_perm(
            "projects.change_dmp", dmp_test_data["dmp_with_project"]
        )

    def test_owner_role_denies_manager(self, dmp_test_data):
        """Test that user with MANAGER role does not have change permission."""
        ProjectMembership.objects.create(
            project=dmp_test_data["project1"],
            user=dmp_test_data["manager_user"],
            role=ProjectMembership.Role.MANAGER,
        )
        assert not dmp_test_data["manager_user"].has_perm(
            "projects.change_dmp", dmp_test_data["dmp_with_project"]
        )

    def test_owner_role_denies_member(self, dmp_test_data):
        """Test that user with MEMBER role does not have change permission."""
        ProjectMembership.objects.create(
            project=dmp_test_data["project1"],
            user=dmp_test_data["member_user"],
            role=ProjectMembership.Role.MEMBER,
        )
        assert not dmp_test_data["member_user"].has_perm(
            "projects.change_dmp", dmp_test_data["dmp_with_project"]
        )

    def test_owner_role_denies_non_member(self, dmp_test_data):
        """Test that non-member user does not have change permission."""
        assert not dmp_test_data["non_member_user"].has_perm(
            "projects.change_dmp", dmp_test_data["dmp_with_project"]
        )

    def test_dmp_owner_can_perform_owner_actions_without_project(self, dmp_test_data):
        """Test that DMP owner has change permission on standalone DMP."""
        assert dmp_test_data["owner_user"].has_perm(
            "projects.change_dmp", dmp_test_data["dmp_without_project"]
        )

    def test_non_dmp_owner_cannot_perform_owner_actions_on_standalone(
        self, dmp_test_data
    ):
        """Test that non-owner does not have change permission on standalone DMP."""
        assert not dmp_test_data["member_user"].has_perm(
            "projects.change_dmp", dmp_test_data["dmp_without_project"]
        )

    def test_data_manager_role_allows_data_manager(self, dmp_test_data):
        """Test that user with DATA_MANAGER role has change permission."""
        ProjectMembership.objects.create(
            project=dmp_test_data["project1"],
            user=dmp_test_data["manager_user"],
            role=ProjectMembership.Role.DATA_MANAGER,
        )
        assert dmp_test_data["manager_user"].has_perm(
            "projects.change_dmp", dmp_test_data["dmp_with_project"]
        )

    def test_manager_role_denies_manager(self, dmp_test_data):
        """Test that user with MANAGER role does not have change permission."""
        ProjectMembership.objects.create(
            project=dmp_test_data["project1"],
            user=dmp_test_data["manager_user"],
            role=ProjectMembership.Role.MANAGER,
        )
        assert not dmp_test_data["manager_user"].has_perm(
            "projects.change_dmp", dmp_test_data["dmp_with_project"]
        )

    def test_member_role_denies_member(self, dmp_test_data):
        """Test that user with MEMBER role does not have change permission."""
        ProjectMembership.objects.create(
            project=dmp_test_data["project1"],
            user=dmp_test_data["member_user"],
            role=ProjectMembership.Role.MEMBER,
        )
        assert not dmp_test_data["member_user"].has_perm(
            "projects.change_dmp", dmp_test_data["dmp_with_project"]
        )

    def test_unauthenticated_user_denied_all_permissions(self, dmp_test_data):
        """Test that unauthenticated user has no change permission."""
        assert not AnonymousUser().has_perm(
            "projects.change_dmp", dmp_test_data["dmp_with_project"]
        )
        assert not AnonymousUser().has_perm(
            "projects.change_dmp", dmp_test_data["dmp_without_project"]
        )
