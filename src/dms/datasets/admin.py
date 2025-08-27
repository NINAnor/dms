from django.contrib import admin

from .models import (
    Dataset,
    MapResource,
    RasterResource,
    Resource,
    TabularResource,
    # PartitionedResource,
)


@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    pass


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    pass


@admin.register(MapResource)
class MapResourceAdmin(admin.ModelAdmin):
    pass


@admin.register(RasterResource)
class RasterResourceAdmin(admin.ModelAdmin):
    pass


@admin.register(TabularResource)
class TabularResourceAdmin(admin.ModelAdmin):
    pass
