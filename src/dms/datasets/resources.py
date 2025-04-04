from import_export import resources


class SchemaResource(resources.ModelResource):
    class Meta:
        model = "datasets.Schema"
        import_id_fields = ("name",)
