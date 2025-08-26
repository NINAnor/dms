import rules

from dms.projects.models import Project


@rules.predicate
def dataset_in_user_projects(user, dataset):
    if not user.is_authenticated:
        return False
    if not dataset:
        return True
    if not dataset.project_id and user.is_staff:
        return True
    return Project.objects.filter(members__user=user, datasets=dataset).exists()


@rules.predicate
def resource_in_user_projects(user, resource):
    if not user.is_authenticated:
        return False
    if not resource:
        return True
    if resource.dataset.project:
        return resource.dataset.project.filter(members__user=user).exists()
    return False
