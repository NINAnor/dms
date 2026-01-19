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
    if not user.is_authenticated:
        return False
    if not instance:
        return True
    return instance.owner == user


@rules.predicate
def is_dmp_project_participant(user, dmp):
    if not user.is_authenticated:
        return False
    if not dmp:
        return True
    if dmp and not dmp.project:
        return dmp.owner == user
    return dmp.project.memberships.filter(id=user.id).exists()


def dmp_project_role_is(role):
    @rules.predicate
    def has_role_in_project(user, dmp):
        if not user.is_authenticated:
            return False
        if not dmp.project and dmp.owner == user:
            return True
        if dmp.project:
            return dmp.project.members.filter(user=user, role=role).exists()
        return False

    return has_role_in_project
