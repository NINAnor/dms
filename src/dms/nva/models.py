from django.db import models


class NVAProject(models.Model):
    id = models.CharField(primary_key=True)
    name = models.CharField(null=True, blank=True)
    projects = models.ManyToManyField(
        "projects.Project", through="NVAProjectRelationship", blank=True
    )

    def __str__(self):
        return self.name or self.id


class NVAProjectRelationship(models.Model):
    pk = models.CompositePrimaryKey("nva_project", "project")
    nva_project = models.ForeignKey(
        "NVAProject", on_delete=models.CASCADE, db_constraint=False
    )
    project = models.ForeignKey(
        "projects.Project", on_delete=models.CASCADE, db_constraint=False
    )


class NVAPublication(models.Model):
    id = models.CharField(primary_key=True)
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title or self.id


class NVAPublicationProject(models.Model):
    pk = models.CompositePrimaryKey("nva_publication", "nva_project")
    nva_publication = models.ForeignKey(
        "NVAPublication", on_delete=models.CASCADE, db_constraint=False
    )
    nva_project = models.ForeignKey(
        "NVAProject", on_delete=models.CASCADE, db_constraint=False
    )


class NVAPublicationDataset(models.Model):
    pk = models.CompositePrimaryKey("nva_publication", "dataset")
    nva_publication = models.ForeignKey(
        "NVAPublication", on_delete=models.CASCADE, db_constraint=False
    )
    dataset = models.ForeignKey(
        "datasets.Dataset", on_delete=models.CASCADE, db_constraint=False
    )
