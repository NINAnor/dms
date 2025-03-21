import rules
from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from rules.contrib.models import RulesModel
from solo.models import SingletonModel
from taggit.managers import TaggableManager

from dms.core.models import GenericStringTaggedItem

from .rules import is_owner, project_role_is

User = get_user_model()


class ProjectsConfiguration(SingletonModel):
    dmp_survey_config = models.ForeignKey(
        "surveys.Survey", on_delete=models.PROTECT, null=True, blank=True
    )

    def __str__(self):
        return self._meta.verbose_name

    class Meta:
        verbose_name = "Projects Configuration"


class ProjectMembership(models.Model):
    class Role(models.TextChoices):
        OWNER = "owner", "Leader"
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


class DMP(RulesModel):
    name = models.CharField()
    data = models.JSONField(null=True, blank=True)
    project = models.OneToOneField(
        "Project", null=True, blank=True, on_delete=models.SET_NULL, related_name="dmp"
    )
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_absolute_url(self):
        return reverse("projects:dmp_detail", kwargs={"pk": self.pk})

    class Meta:
        rules_permissions = {
            "add": rules.is_authenticated,
            "view": rules.always_allow,
            "change": is_owner,
            "delete": is_owner,
        }

    def __str__(self):
        return self.name


class Project(RulesModel):
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

    tags = TaggableManager(through=GenericStringTaggedItem)

    def __str__(self) -> str:
        if self.name:
            return f"{self.number} {self.name}"

        return self.number

    def get_absolute_url(self):
        return reverse("projects:project_detail", kwargs={"pk": self.pk})

    @property
    def leaders(self):
        return User.objects.filter(
            memberships__role=ProjectMembership.Role.OWNER,
            memberships__project_id=self.number,
        )

    class Meta:
        rules_permissions = {
            "add": rules.is_staff,
            "view": rules.always_allow,
            "change": project_role_is(ProjectMembership.Role.OWNER),
            "delete": rules.is_staff,
        }
