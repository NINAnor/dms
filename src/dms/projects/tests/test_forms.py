"""Unit tests for project forms."""

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from dms.projects.forms import DMPForm, ProjectForm
from dms.projects.models import DMP, DMPSchema, Project, ProjectMembership, ProjectTopic

User = get_user_model()


@pytest.mark.django_db(transaction=True)
class TestProjectForm:
    """Test cases for ProjectForm."""

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
    def topic(self):
        """Create a test project topic."""
        return ProjectTopic.objects.create(id="research")

    # ========== Form Validation ==========

    def test_form_valid_data(self, project, topic):
        """Test form with valid data."""
        form_data = {
            "description": "Updated description",
            "topics": [topic.id],
            "tags": "",
        }
        form = ProjectForm(data=form_data)

        assert form.is_valid()

    def test_form_valid_with_tags(self, project, topic):
        """Test form with valid data including tags."""
        form_data = {
            "description": "Updated description",
            "topics": [topic.id],
            "tags": "tag1, tag2",
        }
        form = ProjectForm(data=form_data)

        assert form.is_valid()

    def test_form_valid_without_topics(self, project):
        """Test form with valid data but no topics."""
        form_data = {
            "description": "Updated description",
            "topics": [],
            "tags": "",
        }
        form = ProjectForm(data=form_data)

        assert form.is_valid()

    # ========== Form Instance Handling ==========

    def test_form_with_instance(self, project, topic):
        """Test form initialized with existing instance."""
        form = ProjectForm(instance=project)

        assert form.instance == project
        assert "description" in form.fields

    def test_form_save_with_instance(self, project, topic):
        """Test saving form with instance data."""
        form_data = {
            "description": "New description",
            "topics": [topic.id],
            "tags": "new_tag",
        }
        form = ProjectForm(data=form_data, instance=project)

        if form.is_valid():
            saved_project = form.save()

        assert saved_project.description == "New description"


@pytest.mark.django_db(transaction=True)
class TestDMPForm:
    """Test cases for DMPForm."""

    @pytest.fixture
    def user(self):
        """Create a test user."""
        return User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",  # noqa: S106
        )

    @pytest.fixture
    def owner_user(self):
        """Create a user who owns a project."""
        return User.objects.create_user(
            username="owner",
            email="owner@example.com",
            password="testpass123",  # noqa: S106
        )

    @pytest.fixture
    def project_with_owner(self, owner_user):
        """Create a project with an owner."""
        project = Project.objects.create(
            number="P002",
            name="Test Project",
            description="A test project",
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
    def dmp(self, owner_user, dmp_schema, project_with_owner):
        """Create a test DMP instance."""
        return DMP.objects.create(
            name="Test DMP",
            owner=owner_user,
            schema_from=dmp_schema,
            project=project_with_owner,
        )

    # ========== Project Queryset Filtering ==========

    def test_form_project_queryset_filtered_by_user(self, owner_user):
        """Test that project queryset is filtered by user ownership."""
        schema = DMPSchema.objects.create(
            name="Test Schema",
            config={"pages": []},
        )

        dmp = DMP.objects.create(
            name="Test DMP",
            owner=owner_user,
            schema_from=schema,
        )

        # Create a project where user is owner
        project1 = Project.objects.create(number="P001", start_date=timezone.now())
        ProjectMembership.objects.create(
            project=project1,
            user=owner_user,
            role=ProjectMembership.Role.OWNER,
        )

        # Create a project where user is not owner
        project2 = Project.objects.create(number="P002", start_date=timezone.now())
        ProjectMembership.objects.create(
            project=project2,
            user=owner_user,
            role=ProjectMembership.Role.MEMBER,
        )

        project3 = Project.objects.create(number="P003", start_date=timezone.now())
        project4 = Project.objects.create(number="P004", start_date=timezone.now())
        pm1 = ProjectMembership.objects.create(
            project=project4,
            user=owner_user,
            role=ProjectMembership.Role.MEMBER,
        )
        dmp.project = project4
        dmp.save()

        project5 = Project.objects.create(number="P005", start_date=timezone.now())
        ProjectMembership.objects.create(
            project=project5,
            user=owner_user,
            role=ProjectMembership.Role.DATA_MANAGER,
        )

        form = DMPForm(user=owner_user)
        queryset = form.fields["project"].queryset

        # Only project1 should be in queryset
        assert project1 in queryset
        assert project2 not in queryset
        assert project3 not in queryset
        assert project4 not in queryset
        # Change the role and test it again
        pm1.role = ProjectMembership.Role.DATA_MANAGER
        pm1.save()
        assert project4 not in queryset
        assert project5 in queryset

    def test_form_project_field_empty_for_user_without_projects(self):
        """Test that project queryset is empty for user without owned projects."""
        user_without_projects = User.objects.create_user(
            username="noProjects",
            email="noprojects@example.com",
            password="testpass123",  # noqa: S106
        )
        form = DMPForm(user=user_without_projects)
        queryset = form.fields["project"].queryset

        # Queryset should be empty
        assert queryset.count() == 0

    # ========== Schema From Field Handling ==========

    def test_form_schema_from_deletion(self, owner_user, dmp_schema, dmp):
        """Test that schema_from field is deleted when present in instance."""
        form = DMPForm(user=owner_user, instance=dmp)
        # schema_from should be removed from fields
        assert "schema_from" not in form.fields

    # ========== Form Validation ==========

    def test_form_valid_data(self, owner_user, dmp_schema, project_with_owner):
        """Test form with valid data."""
        form_data = {
            "name": "New DMP",
            "schema_from": dmp_schema.id,
            "project": project_with_owner.number,
            "external_reference": "",
            "external_file": "",
        }
        form = DMPForm(data=form_data, user=owner_user)

        assert form.is_valid()

    def test_form_valid_with_external_reference(
        self, owner_user, dmp_schema, project_with_owner
    ):
        """Test form with external reference."""
        form_data = {
            "name": "External DMP",
            "schema_from": dmp_schema.id,
            "project": project_with_owner.number,
            "external_reference": "https://example.com/dmp",
            "external_file": "",
        }
        form = DMPForm(data=form_data, user=owner_user)

        assert form.is_valid()

    # ========== Form Save Behavior ==========

    def test_form_save_sets_owner(self, owner_user, dmp_schema, project_with_owner):
        """Test that form.save() sets the owner to the current user."""
        form_data = {
            "name": "DMP with Owner",
            "schema_from": dmp_schema.id,
            "project": project_with_owner.number,
            "external_reference": "",
            "external_file": "",
        }
        form = DMPForm(data=form_data, user=owner_user)

        if form.is_valid():
            dmp = form.save()
            assert dmp.owner == owner_user

    def test_form_save_copies_schema_from_config(
        self, owner_user, dmp_schema, project_with_owner
    ):
        """Test that form.save() copies schema from schema_from config."""
        form_data = {
            "name": "DMP with Schema",
            "schema_from": dmp_schema.id,
            "project": project_with_owner.number,
            "external_reference": "",
            "external_file": "",
        }
        form = DMPForm(data=form_data, user=owner_user)

        if form.is_valid():
            dmp = form.save()
            assert dmp.schema == dmp_schema.config
