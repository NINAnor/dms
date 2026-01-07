"""Unit tests for project models custom methods."""

import pytest
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.utils import timezone

from dms.projects.models import DMP, DMPSchema, Project, ProjectMembership

User = get_user_model()


@pytest.mark.django_db(transaction=True)
class TestProjectModel:
    """Test cases for Project model custom methods."""

    @pytest.fixture
    def project(self):
        """Create a test project."""
        return Project.objects.create(
            number="P001",
            name="Test Project",
            description="A test project",
            start_date=timezone.now(),
        )

    @pytest.fixture
    def project_without_name(self):
        """Create a test project without a name."""
        return Project.objects.create(
            number="P002",
            start_date=timezone.now(),
        )

    @pytest.fixture
    def owner_user(self):
        """Create a user who will be a project owner."""
        return User.objects.create_user(
            username="owner",
            email="owner@example.com",
            password="testpass123",  # noqa: S106
        )

    @pytest.fixture
    def member_user(self):
        """Create a user who will be a project member."""
        return User.objects.create_user(
            username="member",
            email="member@example.com",
            password="testpass123",  # noqa: S106
        )

    @pytest.fixture
    def manager_user(self):
        """Create a user who will be a project manager."""
        return User.objects.create_user(
            username="manager",
            email="manager@example.com",
            password="testpass123",  # noqa: S106
        )

    # ========== __str__ Method ==========

    def test_project_str_with_name(self, project):
        """Test that __str__ returns 'number name' when name is present."""
        assert str(project) == "P001 Test Project"

    def test_project_str_without_name(self, project_without_name):
        """Test that __str__ returns just number when name is absent."""
        assert str(project_without_name) == "P002"

    # ========== get_absolute_url Method ==========

    def test_project_get_absolute_url(self, project):
        """Test that get_absolute_url returns correct URL."""
        url = project.get_absolute_url()
        assert url == "/projects/P001/"
        assert "projects" in url
        assert "project_detail" in url or "P001" in url

    # ========== leaders Property ==========

    def test_project_leaders_returns_owner_only(self, project, owner_user, member_user):
        """Test that leaders property returns only owner users."""
        ProjectMembership.objects.create(
            project=project,
            user=owner_user,
            role=ProjectMembership.Role.OWNER,
        )
        ProjectMembership.objects.create(
            project=project,
            user=member_user,
            role=ProjectMembership.Role.MEMBER,
        )

        leaders = project.leaders
        assert owner_user in leaders
        assert member_user not in leaders
        assert leaders.count() == 1

    def test_project_leaders_excludes_managers(self, project, owner_user, manager_user):
        """Test that leaders property excludes managers."""
        ProjectMembership.objects.create(
            project=project,
            user=owner_user,
            role=ProjectMembership.Role.OWNER,
        )
        ProjectMembership.objects.create(
            project=project,
            user=manager_user,
            role=ProjectMembership.Role.MANAGER,
        )

        leaders = project.leaders
        assert owner_user in leaders
        assert manager_user not in leaders

    def test_project_leaders_multiple_owners(self, project):
        """Test that leaders returns all owner-level members."""
        owner1 = User.objects.create_user(
            username="owner1",
            email="owner1@example.com",
            password="testpass123",  # noqa: S106
        )
        owner2 = User.objects.create_user(
            username="owner2",
            email="owner2@example.com",
            password="testpass123",  # noqa: S106
        )

        ProjectMembership.objects.create(
            project=project,
            user=owner1,
            role=ProjectMembership.Role.OWNER,
        )
        ProjectMembership.objects.create(
            project=project,
            user=owner2,
            role=ProjectMembership.Role.OWNER,
        )

        leaders = project.leaders
        assert leaders.count() == 2
        assert owner1 in leaders
        assert owner2 in leaders

    def test_project_leaders_no_members(self, project):
        """Test that leaders returns empty queryset when no owners."""
        leaders = project.leaders
        assert leaders.count() == 0

    def test_project_leaders_different_project(self, owner_user):
        """Test that leaders only returns members of specific project."""
        project1 = Project.objects.create(
            number="P001",
            start_date=timezone.now(),
        )
        project2 = Project.objects.create(
            number="P002",
            start_date=timezone.now(),
        )

        ProjectMembership.objects.create(
            project=project1,
            user=owner_user,
            role=ProjectMembership.Role.OWNER,
        )

        # project2 should have no leaders
        assert project2.leaders.count() == 0
        # project1 should have one leader
        assert project1.leaders.count() == 1


@pytest.mark.django_db(transaction=True)
class TestDMPModel:
    """Test cases for DMP model custom methods."""

    @pytest.fixture
    def owner_user(self):
        """Create an owner user."""
        return User.objects.create_user(
            username="owner",
            email="owner@example.com",
            password="testpass123",  # noqa: S106
        )

    @pytest.fixture
    def project(self, owner_user):
        """Create a project with an owner."""
        project = Project.objects.create(
            number="P001",
            name="Test Project",
            start_date=timezone.now(),
        )
        ProjectMembership.objects.create(
            project=project,
            user=owner_user,
            role=ProjectMembership.Role.OWNER,
        )
        return project

    @pytest.fixture
    def dmp_schema(self):
        """Create a test DMP schema."""
        return DMPSchema.objects.create(
            name="Test Schema",
            config={"pages": []},
        )

    @pytest.fixture
    def dmp_basic(self, owner_user, project, dmp_schema):
        """Create a basic DMP without external references."""
        return DMP.objects.create(
            name="Basic DMP",
            owner=owner_user,
            project=project,
            schema_from=dmp_schema,
        )

    @pytest.fixture
    def dmp_with_external_reference(self, owner_user, project, dmp_schema):
        """Create a DMP with an external reference."""
        return DMP.objects.create(
            name="External Reference DMP",
            owner=owner_user,
            project=project,
            schema_from=dmp_schema,
            external_reference="https://example.com/dmp",
        )

    @pytest.fixture
    def dmp_with_external_file(self, owner_user, project, dmp_schema):
        """Create a DMP with an external file."""
        dmp = DMP.objects.create(
            name="External File DMP",
            owner=owner_user,
            project=project,
            schema_from=dmp_schema,
        )
        dmp.external_file.save(
            "test.pdf",
            ContentFile(b"Test file content"),
        )
        return dmp

    # ========== __str__ Method ==========

    def test_dmp_str(self, dmp_basic):
        """Test that __str__ returns the DMP name."""
        assert str(dmp_basic) == "Basic DMP"

    # ========== get_absolute_url Method ==========

    def test_dmp_get_absolute_url(self, dmp_basic):
        """Test that get_absolute_url returns correct URL."""
        url = dmp_basic.get_absolute_url()
        assert "dmp_detail" in url or str(dmp_basic.pk) in url
        assert url.startswith("/")

    def test_dmp_get_absolute_url_different_pk(self, dmp_with_external_reference):
        """Test get_absolute_url with different DMP."""
        url = dmp_with_external_reference.get_absolute_url()
        assert str(dmp_with_external_reference.pk) in url

    # ========== is_external Property ==========

    def test_is_external_false_without_external_data(self, dmp_basic):
        """Test that is_external is False when no external data exists."""
        assert dmp_basic.is_external is False

    def test_is_external_true_with_external_reference(
        self, dmp_with_external_reference
    ):
        """Test that is_external is True when external_reference is set."""
        assert dmp_with_external_reference.is_external is True

    def test_is_external_true_with_external_file(self, dmp_with_external_file):
        """Test that is_external is True when external_file is set."""
        assert dmp_with_external_file.is_external is True

    def test_is_external_true_with_both(self, owner_user, project, dmp_schema):
        """Test that is_external is True when both reference and file exist."""
        dmp = DMP.objects.create(
            name="Both External DMP",
            owner=owner_user,
            project=project,
            schema_from=dmp_schema,
            external_reference="https://example.com/dmp",
        )
        dmp.external_file.save(
            "test.pdf",
            ContentFile(b"Test file content"),
        )

        assert dmp.is_external is True

    def test_is_external_false_with_empty_file_field(
        self, owner_user, project, dmp_schema
    ):
        """Test that is_external is False when file field is empty."""
        dmp = DMP.objects.create(
            name="Empty File DMP",
            owner=owner_user,
            project=project,
            schema_from=dmp_schema,
        )
        # external_file is not set (None or empty)
        assert dmp.is_external is False

    def test_is_external_false_with_empty_reference(
        self, owner_user, project, dmp_schema
    ):
        """Test that is_external is False when reference is empty string."""
        dmp = DMP.objects.create(
            name="Empty Reference DMP",
            owner=owner_user,
            project=project,
            schema_from=dmp_schema,
            external_reference="",
        )
        assert dmp.is_external is False


@pytest.mark.django_db(transaction=True)
class TestProjectMembershipModel:
    """Test cases for ProjectMembership model custom methods."""

    @pytest.fixture
    def project(self):
        """Create a test project."""
        return Project.objects.create(
            number="P001",
            name="Test Project",
            start_date=timezone.now(),
        )

    @pytest.fixture
    def user(self):
        """Create a test user."""
        return User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",  # noqa: S106
        )

    # ========== __str__ Method ==========

    def test_membership_str_owner_role(self, project, user):
        """Test __str__ for membership with owner role."""
        membership = ProjectMembership.objects.create(
            project=project,
            user=user,
            role=ProjectMembership.Role.OWNER,
        )

        str_repr = str(membership)
        assert project.number in str_repr
        assert user.username in str_repr
        assert "Leader" in str_repr

    def test_membership_str_manager_role(self, project, user):
        """Test __str__ for membership with manager role."""
        membership = ProjectMembership.objects.create(
            project=project,
            user=user,
            role=ProjectMembership.Role.MANAGER,
        )

        str_repr = str(membership)
        assert project.number in str_repr
        assert user.username in str_repr
        assert "Manager" in str_repr

    def test_membership_str_member_role(self, project, user):
        """Test __str__ for membership with member role."""
        membership = ProjectMembership.objects.create(
            project=project,
            user=user,
            role=ProjectMembership.Role.MEMBER,
        )

        str_repr = str(membership)
        assert project.number in str_repr
        assert user.username in str_repr
        assert "Member" in str_repr

    def test_membership_str_format(self, project, user):
        """Test that __str__ format is consistent."""
        membership = ProjectMembership.objects.create(
            project=project,
            user=user,
            role=ProjectMembership.Role.OWNER,
        )

        # Format should be "project_id user - role_display"
        str_repr = str(membership)
        assert " - " in str_repr
        assert str_repr.startswith(project.number)
