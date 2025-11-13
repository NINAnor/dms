from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from ..models import (
    Dataset,
    DatasetRelationship,
    DataTable,
    MapResource,
    PartitionedResource,
    RasterResource,
    Resource,
    TabularResource,
)


class DatasetGeoSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = Dataset
        fields = (
            "id",
            "title",
        )
        geo_field = "extent"


class DatasetSerializer(serializers.HyperlinkedModelSerializer):
    project = serializers.HyperlinkedRelatedField(
        view_name="api_v1:projects-detail", read_only=True
    )
    project_id = serializers.CharField()
    url = serializers.HyperlinkedIdentityField(view_name="api_v1:datasets-detail")

    class Meta:
        model = Dataset
        fields = (
            "url",
            "id",
            "title",
            "name",
            "created_at",
            "last_modified_at",
            "project",
            "project_id",
            "metadata",
            "version",
        )


class DatasetListSerializer(DatasetSerializer):
    class Meta:
        model = Dataset
        fields = (
            "url",
            "id",
            "title",
            "name",
            "created_at",
            "last_modified_at",
            "project",
            "project_id",
            "version",
        )


class ResourceListSerializer(serializers.HyperlinkedModelSerializer):
    dataset = serializers.HyperlinkedRelatedField(
        view_name="api_v1:datasets-detail", read_only=True
    )
    url = serializers.HyperlinkedIdentityField(view_name="api_v1:resources-detail")
    dataset_id = serializers.CharField()

    titiler = serializers.JSONField(read_only=True)

    class Meta:
        model = Resource
        fields = (
            "url",
            "id",
            "title",
            "uri",
            "created_at",
            "last_modified_at",
            "dataset_id",
            "dataset",
            "role",
            "access_type",
            "description",
        )


class ResourceSerializer(ResourceListSerializer):
    class Meta(ResourceListSerializer.Meta):
        fields = ResourceListSerializer.Meta.fields + ("metadata", "last_sync")


class ResourceGeoSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = Resource
        fields = (
            "id",
            "title",
        )
        geo_field = "extent"


class DatasetRelationshipSerializer(serializers.HyperlinkedModelSerializer):
    source = serializers.HyperlinkedRelatedField(
        view_name="api_v1:datasets-detail", read_only=True
    )
    target = serializers.HyperlinkedRelatedField(
        view_name="api_v1:datasets-detail", read_only=True
    )

    class Meta:
        model = DatasetRelationship
        fields = ("source", "source_id", "target", "target_id", "type", "uuid", "url")
        extra_kwargs = {
            "url": {
                "view_name": "api_v1:dataset-relationships-detail",
                "lookup_field": "uuid",
            }
        }


class DatasetRelationshipCreateSerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField(read_only=True)

    class Meta:
        model = DatasetRelationship
        fields = (
            "url",
            "uuid",
            "source",
            "target",
            "type",
        )
        extra_kwargs = {
            "url": {
                "view_name": "api_v1:dataset-relationships-detail",
                "lookup_field": "uuid",
            }
        }


class MapResourceSerializer(serializers.HyperlinkedModelSerializer):
    dataset = serializers.HyperlinkedRelatedField(
        view_name="api_v1:datasets-detail", read_only=True
    )
    dataset_id = serializers.CharField()
    url = serializers.HyperlinkedIdentityField(view_name="api_v1:mapresources-detail")

    class Meta:
        model = MapResource
        fields = ResourceSerializer.Meta.fields + ("map_type",)


class RasterResourceSerializer(serializers.HyperlinkedModelSerializer):
    dataset = serializers.HyperlinkedRelatedField(
        view_name="api_v1:datasets-detail", read_only=True
    )
    url = serializers.HyperlinkedIdentityField(
        view_name="api_v1:rasterresources-detail"
    )
    dataset_id = serializers.CharField()

    class Meta:
        model = RasterResource
        fields = ResourceSerializer.Meta.fields + ("titiler",)


class TabularResourceSerializer(serializers.HyperlinkedModelSerializer):
    dataset = serializers.HyperlinkedRelatedField(
        view_name="api_v1:datasets-detail", read_only=True
    )
    url = serializers.HyperlinkedIdentityField(
        view_name="api_v1:tabularresources-detail"
    )
    dataset_id = serializers.CharField()

    class Meta:
        model = TabularResource
        fields = ResourceSerializer.Meta.fields


class PartitionedResourceSerializer(serializers.HyperlinkedModelSerializer):
    dataset = serializers.HyperlinkedRelatedField(
        view_name="api_v1:datasets-detail", read_only=True
    )
    url = serializers.HyperlinkedIdentityField(
        view_name="api_v1:partitionedresources-detail"
    )
    dataset_id = serializers.CharField()

    class Meta:
        model = PartitionedResource
        fields = ResourceSerializer.Meta.fields


class DataTableListSerializer(serializers.HyperlinkedModelSerializer):
    resource = serializers.HyperlinkedRelatedField(
        view_name="api_v1:resources-detail", read_only=True
    )
    resource_id = serializers.CharField()

    driver = serializers.CharField(
        read_only=True, source="resource__metadata__driverShortName"
    )

    # url = serializers.SerializerMethodField(
    #     view_name="api_v1:datatables-detail", lookup_field=("resource", "name")
    # )

    class Meta:
        model = DataTable
        fields = (
            "name",
            "resource",
            "resource_id",
            "is_spatial",
            "driver",
            "count",
            # "url",
        )


class DataTableSerializer(DataTableListSerializer):
    class Meta(DataTableListSerializer.Meta):
        fields = DataTableListSerializer.Meta.fields + (
            "fields",
            "extent",
            "geometryFields",
            "metadata",
        )
