import rules


def project_role_is(role):
    @rules.predicate
    def has_role_in_project(user, project):
        return project.members.filter(user=user, role=role).exists()

    return has_role_in_project


@rules.predicate
def is_project_participant(user, project):
    return project.memberships.filter(user=user).exists()
