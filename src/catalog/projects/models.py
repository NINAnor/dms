from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from taggit.managers import TaggableManager

User = get_user_model()


class ProjectMembership(models.Model):
    class Role(models.TextChoices):
        OWNER = "owner", "Owner"
        MANAGER = "manager", "Manager"
        MEMBER = "member", "Member"

    project = models.ForeignKey(
        "Project", on_delete=models.CASCADE, related_name="members", db_constraint=False
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="memberships", db_constraint=False
    )
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


class Category(models.Model):
    text = models.CharField()

    def __str__(self):
        return self.text


class Section(models.Model):
    id = models.CharField(primary_key=True)
    text = models.CharField()

    def __str__(self):
        return self.text


class Topic(models.Model):
    text = models.CharField()

    def __str__(self):
        return self.text


class Project(models.Model):
    number = models.CharField(primary_key=True)
    name = models.CharField(null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    memberships = models.ManyToManyField(
        "users.User", through="ProjectMembership", blank=True
    )
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(blank=True, null=True)
    status = models.CharField(null=True, blank=True)
    category = models.ForeignKey(
        "Category",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_constraint=False,
    )
    section = models.ForeignKey(
        "Section", on_delete=models.SET_NULL, null=True, blank=True, db_constraint=False
    )
    customer = models.CharField(null=True, blank=True)
    budget = models.DecimalField(decimal_places=2, max_digits=16, null=True, blank=True)

    description = models.TextField(blank=True, null=True)
    topics = models.ManyToManyField("Topic", blank=True)

    tags = TaggableManager()

    def __str__(self) -> str:
        if self.name:
            return f"{self.number} {self.name}"

        return self.number

    def get_absolute_url(self):
        return reverse("projects:project-detail", kwargs={"pk": self.pk})
