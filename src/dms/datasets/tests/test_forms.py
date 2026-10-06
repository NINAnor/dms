import uuid

import pytest
from django.utils import timezone
from django.utils.datastructures import MultiValueDict

from dms.datasets.forms import ResourceForm
from dms.datasets.models import Dataset, Resource
from dms.datasets.tests.test_models import _make_storage
from dms.projects.models import Project


def _form_data(**fields):
    return MultiValueDict({key: [value] for key, value in fields.items()})


@pytest.fixture
def project():
    return Project.objects.create(
        number="DS003",
        name="Form Test Project",
        start_date=timezone.now(),
    )


@pytest.fixture
def dataset(project):
    return Dataset.objects.create(title="Form Test Dataset", project=project)


@pytest.fixture
def user(django_user_model):
    return django_user_model.objects.create_user(
        username="formtestuser", email="formtestuser@example.com"
    )


@pytest.mark.django_db(transaction=True)
class TestResourceFormUriReadOnlyForDirectUpload:
    """A direct-upload resource's uri is derived server-side and must stay
    read-only once storage/key are set, in the HTML edit forms too."""

    def test_uri_field_disabled_for_direct_upload_resource(self, dataset, user):
        storage = _make_storage()
        resource = Resource.objects.create(
            id=uuid.uuid4(),
            uri="https://example.com/original",
            dataset=dataset,
            storage=storage,
            key="some/key.txt",
        )

        form = ResourceForm(instance=resource, user=user, dataset=dataset)

        assert form.fields["uri"].disabled

    def test_posted_uri_is_ignored_for_direct_upload_resource(self, dataset, user):
        storage = _make_storage()
        resource = Resource.objects.create(
            id=uuid.uuid4(),
            uri="https://example.com/original",
            dataset=dataset,
            storage=storage,
            key="some/key.txt",
        )

        form = ResourceForm(
            data=_form_data(
                title="Resource",
                uri="https://example.com/changed",
                role=resource.role,
                access_type=resource.access_type,
            ),
            instance=resource,
            user=user,
            dataset=dataset,
        )

        # A disabled field ignores posted data and falls back to its
        # initial value, so the uri is left untouched either way.
        assert form.is_valid(), form.errors
        assert form.cleaned_data["uri"] == "https://example.com/original"

    def test_uri_can_be_resubmitted_unchanged_for_direct_upload_resource(
        self, dataset, user
    ):
        storage = _make_storage()
        resource = Resource.objects.create(
            id=uuid.uuid4(),
            uri="https://example.com/original",
            dataset=dataset,
            storage=storage,
            key="some/key.txt",
        )

        form = ResourceForm(
            data=_form_data(
                title="Resource",
                uri="https://example.com/original",
                role=resource.role,
                access_type=resource.access_type,
            ),
            instance=resource,
            user=user,
            dataset=dataset,
        )

        assert form.is_valid(), form.errors

    def test_uri_can_be_changed_for_non_direct_upload_resource(self, dataset, user):
        resource = Resource.objects.create(
            id=uuid.uuid4(),
            uri="not-a-url",
            dataset=dataset,
        )

        form = ResourceForm(
            data=_form_data(
                title="Resource",
                uri="https://example.com/new",
                role=resource.role,
                access_type=resource.access_type,
            ),
            instance=resource,
            user=user,
            dataset=dataset,
        )

        assert form.is_valid(), form.errors

    def test_uri_can_be_set_on_create(self, dataset, user):
        form = ResourceForm(
            data=_form_data(
                title="New Resource",
                uri="https://example.com/new",
                role="data",
                access_type="public",
            ),
            user=user,
            dataset=dataset,
        )

        assert form.is_valid(), form.errors
