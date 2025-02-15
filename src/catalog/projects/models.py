from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class ProjectMembership(models.Model):
    class Role(models.TextChoices):
        OWNER = "owner", "Owner"
        MANAGER = "manager", "Manager"
        MEMBER = "member", "Member"

    project = models.ForeignKey(
        "Project", on_delete=models.CASCADE, related_name="members"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="memberships")
    role = models.CharField(
        choices=Role,
        default=Role.MEMBER,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["project", "user"], name="unique_user_per_project"
            )
        ]

    def __str__(self) -> str:
        return f"{self.project_id} {self.user} - {self.get_role_display()}"


class Project(models.Model):
    number = models.CharField(primary_key=True)
    name = models.CharField(null=True, blank=True)
    memberships = models.ManyToManyField(
        "users.User", through="ProjectMembership", blank=True
    )
    active = models.BooleanField(default=True)

    def __str__(self) -> str:
        if self.name:
            return f"{self.number} {self.name}"

        return self.number
