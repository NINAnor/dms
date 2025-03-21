import rules


def project_role_is(role):
    @rules.predicate
    def has_role_in_project(user, project):
        if project:
            return project.members.filter(user=user, role=role).exists()

        return True

    return has_role_in_project


@rules.predicate
def is_project_participant(user, project):
    return project.memberships.filter(user=user).exists()


@rules.predicate
def is_owner(user, instance):
    return instance.owner == user
