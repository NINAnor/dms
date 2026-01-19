"""Unit tests for DMP rules and permissions."""

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.utils import timezone

from dms.projects.models import DMP, DMPSchema, Project, ProjectMembership

from ..rules import dmp_project_role_is, is_dmp_project_participant

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
class TestIsDmpProjectParticipant:
    """Test cases for is_dmp_project_participant predicate."""

    def test_authenticated_user_in_project_is_participant(self, dmp_test_data):
        """Test that authenticated user in project is considered a participant."""
        ProjectMembership.objects.create(
            project=dmp_test_data["project1"],
            user=dmp_test_data["owner_user"],
            role=ProjectMembership.Role.OWNER,
        )
        predicate = is_dmp_project_participant
        assert (
            predicate(dmp_test_data["owner_user"], dmp_test_data["dmp_with_project"])
            is True
        )

    def test_member_user_in_project_is_participant(self, dmp_test_data):
        """Test that project member is considered a participant."""
        ProjectMembership.objects.create(
            project=dmp_test_data["project1"],
            user=dmp_test_data["member_user"],
            role=ProjectMembership.Role.MEMBER,
        )
        predicate = is_dmp_project_participant
        assert (
            predicate(dmp_test_data["member_user"], dmp_test_data["dmp_with_project"])
            is True
        )

    def test_user_not_in_project_is_not_participant(self, dmp_test_data):
        """Test that user not in project is not a participant."""
        predicate = is_dmp_project_participant
        assert (
            predicate(
                dmp_test_data["non_member_user"], dmp_test_data["dmp_with_project"]
            )
            is False
        )

    def test_unauthenticated_user_is_not_participant(self, dmp_test_data):
        """Test that unauthenticated user is not a participant."""
        unauthenticated_user = AnonymousUser()
        predicate = is_dmp_project_participant
        assert (
            predicate(unauthenticated_user, dmp_test_data["dmp_with_project"]) is False
        )

    def test_standalone_dmp_allows_any_authenticated_user(self, dmp_test_data):
        """Test that standalone DMP (no project) does not allow any authenticated user."""  # noqa: E501
        predicate = is_dmp_project_participant
        assert (
            predicate(
                dmp_test_data["non_member_user2"], dmp_test_data["dmp_without_project"]
            )
            is False
        )

    def test_dmp_with_none_project_allows_authenticated_user(self, dmp_test_data):
        """Test that DMP with None project allows owner"""
        dmp = DMP.objects.create(
            name="DMP with None Project",
            owner=dmp_test_data["owner_user"],
            schema_from=dmp_test_data["schema"],
            project=None,
        )
        predicate = is_dmp_project_participant
        assert predicate(dmp_test_data["owner_user"], dmp) is True

    def test_manager_is_participant(self, dmp_test_data):
        """Test that project manager is a participant."""
        ProjectMembership.objects.create(
            project=dmp_test_data["project1"],
            user=dmp_test_data["manager_user"],
            role=ProjectMembership.Role.MANAGER,
        )
        predicate = is_dmp_project_participant
        assert (
            predicate(dmp_test_data["manager_user"], dmp_test_data["dmp_with_project"])
            is True
        )


@pytest.mark.django_db(transaction=True)
class TestDmpProjectRoleIs:
    """Test cases for dmp_project_role_is predicate factory."""

    def test_owner_role_allows_project_owner(self, dmp_test_data):
        """Test that user with OWNER role in project can perform owner actions."""
        ProjectMembership.objects.create(
            project=dmp_test_data["project1"],
            user=dmp_test_data["owner_user"],
            role=ProjectMembership.Role.OWNER,
        )
        predicate = dmp_project_role_is(ProjectMembership.Role.OWNER)
        assert (
            predicate(dmp_test_data["owner_user"], dmp_test_data["dmp_with_project"])
            is True
        )

    def test_owner_role_denies_manager(self, dmp_test_data):
        """Test that user with MANAGER role cannot perform owner actions."""
        ProjectMembership.objects.create(
            project=dmp_test_data["project1"],
            user=dmp_test_data["manager_user"],
            role=ProjectMembership.Role.MANAGER,
        )
        predicate = dmp_project_role_is(ProjectMembership.Role.OWNER)
        assert (
            predicate(dmp_test_data["manager_user"], dmp_test_data["dmp_with_project"])
            is False
        )

    def test_owner_role_denies_member(self, dmp_test_data):
        """Test that user with MEMBER role cannot perform owner actions."""
        ProjectMembership.objects.create(
            project=dmp_test_data["project1"],
            user=dmp_test_data["member_user"],
            role=ProjectMembership.Role.MEMBER,
        )
        predicate = dmp_project_role_is(ProjectMembership.Role.OWNER)
        assert (
            predicate(dmp_test_data["member_user"], dmp_test_data["dmp_with_project"])
            is False
        )

    def test_owner_role_denies_non_member(self, dmp_test_data):
        """Test that non-member user cannot perform owner actions."""
        predicate = dmp_project_role_is(ProjectMembership.Role.OWNER)
        assert (
            predicate(
                dmp_test_data["non_member_user"], dmp_test_data["dmp_with_project"]
            )
            is False
        )

    def test_dmp_owner_can_perform_owner_actions_without_project(self, dmp_test_data):
        """Test that DMP owner can perform owner actions on standalone DMP."""
        predicate = dmp_project_role_is(ProjectMembership.Role.OWNER)
        assert (
            predicate(dmp_test_data["owner_user"], dmp_test_data["dmp_without_project"])
            is True
        )

    def test_non_dmp_owner_cannot_perform_owner_actions_on_standalone(
        self, dmp_test_data
    ):
        """Test that non-owner cannot perform owner actions on standalone DMP."""
        predicate = dmp_project_role_is(ProjectMembership.Role.OWNER)
        assert (
            predicate(
                dmp_test_data["member_user"], dmp_test_data["dmp_without_project"]
            )
            is False
        )

    def test_manager_role_allows_manager(self, dmp_test_data):
        """Test that user with MANAGER role can perform manager actions."""
        ProjectMembership.objects.create(
            project=dmp_test_data["project1"],
            user=dmp_test_data["manager_user"],
            role=ProjectMembership.Role.MANAGER,
        )
        predicate = dmp_project_role_is(ProjectMembership.Role.MANAGER)
        assert (
            predicate(dmp_test_data["manager_user"], dmp_test_data["dmp_with_project"])
            is True
        )

    def test_manager_role_allows_owner(self, dmp_test_data):
        """Test that user with OWNER role cannot perform manager-only actions."""
        ProjectMembership.objects.create(
            project=dmp_test_data["project1"],
            user=dmp_test_data["owner_user"],
            role=ProjectMembership.Role.OWNER,
        )
        predicate = dmp_project_role_is(ProjectMembership.Role.MANAGER)
        assert (
            predicate(dmp_test_data["owner_user"], dmp_test_data["dmp_with_project"])
            is False
        )

    def test_manager_role_denies_member(self, dmp_test_data):
        """Test that user with MEMBER role cannot perform manager actions."""
        ProjectMembership.objects.create(
            project=dmp_test_data["project1"],
            user=dmp_test_data["member_user"],
            role=ProjectMembership.Role.MEMBER,
        )
        predicate = dmp_project_role_is(ProjectMembership.Role.MANAGER)
        assert (
            predicate(dmp_test_data["member_user"], dmp_test_data["dmp_with_project"])
            is False
        )

    def test_member_role_allows_member(self, dmp_test_data):
        """Test that user with MEMBER role can perform member actions."""
        ProjectMembership.objects.create(
            project=dmp_test_data["project1"],
            user=dmp_test_data["member_user"],
            role=ProjectMembership.Role.MEMBER,
        )
        predicate = dmp_project_role_is(ProjectMembership.Role.MEMBER)
        assert (
            predicate(dmp_test_data["member_user"], dmp_test_data["dmp_with_project"])
            is True
        )

    def test_member_role_denies_non_member(self, dmp_test_data):
        """Test that non-member user cannot perform member actions."""
        predicate = dmp_project_role_is(ProjectMembership.Role.MEMBER)
        assert (
            predicate(
                dmp_test_data["non_member_user"], dmp_test_data["dmp_with_project"]
            )
            is False
        )

    def test_unauthenticated_user_denied_all_roles(self, dmp_test_data):
        """Test that unauthenticated user is denied all role-based actions."""
        unauthenticated_user = AnonymousUser()

        for role in [
            ProjectMembership.Role.OWNER,
            ProjectMembership.Role.MANAGER,
            ProjectMembership.Role.MEMBER,
        ]:
            predicate = dmp_project_role_is(role)
            assert (
                predicate(unauthenticated_user, dmp_test_data["dmp_with_project"])
                is False
            )
