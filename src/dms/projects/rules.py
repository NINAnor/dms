import rules


def project_role_is(role):
    @rules.predicate
    def has_role_in_project(user, project):
        if not user.is_authenticated:
            return False
        if project:
            return project.members.filter(user=user, role=role).exists()

        return False

    return has_role_in_project


@rules.predicate
def is_project_participant(user, project):
    if not user.is_authenticated:
        return False
    if not project:
        return True
    return project.memberships.filter(user=user).exists()


@rules.predicate
def is_owner(user, instance):
    if not instance:
        return True
    return instance.owner == user


@rules.predicate
def is_protected(user, instance):
    if not instance:
        return True
    return instance.protected


def dmp_project_role_is(role):
    @rules.predicate
    def has_role_in_project(user, dmp):
        if user.is_authenticated and dmp and dmp.project:
            return dmp.project.members.filter(user=user, role=role).exists()
        return False

    return has_role_in_project
