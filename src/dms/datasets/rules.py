import rules

from dms.projects.models import Project


@rules.predicate
def dataset_in_user_projects(user, dataset):
    if not user.is_authenticated:
        return False
    if not dataset:
        return True
    return Project.objects.filter(members__user=user, datasets=dataset).exists()


@rules.predicate
def storage_in_user_projects(user, storage):
    if not user.is_authenticated:
        return False
    if not storage:
        return True
    return Project.objects.filter(members__user=user, storages=storage).exists()


@rules.predicate
def storage_is_shared(user, storage):
    if not user.is_authenticated:
        return False
    if not storage:
        return True
    return storage.project_id is None


@rules.predicate
def resource_in_user_projects(user, resource):
    if not user.is_authenticated:
        return False
    if not resource:
        return True
    return resource.dataset.project.filter(members__user=user).exists()
