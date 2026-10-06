from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from buckets.models import Storage

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
        auto_bbox = True


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


class DirectUploadUriReadOnlyMixin:
    """Prevent editing `uri` for resources created via direct upload.

    Such resources have both `storage` and `key` set server-side when the
    upload is confirmed; their `uri` is derived from storage/key and must
    not be overwritten by the client afterwards.
    """

    def validate_uri(self, value):
        if (
            self.instance is not None
            and self.instance.storage_id is not None
            and self.instance.key is not None
            and value != self.instance.uri
        ):
            raise serializers.ValidationError(
                "uri cannot be changed for resources created via direct upload."
            )
        return value


class ResourceListSerializer(
    DirectUploadUriReadOnlyMixin, serializers.HyperlinkedModelSerializer
):
    dataset = serializers.HyperlinkedRelatedField(
        view_name="api_v1:datasets-detail", read_only=True
    )
    url = serializers.HyperlinkedIdentityField(view_name="api_v1:resources-detail")
    dataset_id = serializers.CharField()

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

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Hide URI if the dataset is under embargo
        if instance.dataset.under_embargo:
            data["uri"] = None
        return data


class ResourceSerializer(ResourceListSerializer):
    class Meta(ResourceListSerializer.Meta):
        fields = ResourceListSerializer.Meta.fields + (
            "metadata",
            "user_metadata",
            "is_metadata_manual",
            "last_sync",
        )


class ResourceGeoSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = Resource
        fields = (
            "id",
            "title",
        )
        geo_field = "extent"
        auto_bbox = True


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


class MapResourceSerializer(
    DirectUploadUriReadOnlyMixin, serializers.HyperlinkedModelSerializer
):
    dataset = serializers.HyperlinkedRelatedField(
        view_name="api_v1:datasets-detail", read_only=True
    )
    dataset_id = serializers.CharField()
    url = serializers.HyperlinkedIdentityField(view_name="api_v1:mapresources-detail")

    class Meta:
        model = MapResource
        fields = ResourceSerializer.Meta.fields + ("map_type",)


class RasterResourceSerializer(
    DirectUploadUriReadOnlyMixin, serializers.HyperlinkedModelSerializer
):
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


class TabularResourceSerializer(
    DirectUploadUriReadOnlyMixin, serializers.HyperlinkedModelSerializer
):
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


class PartitionedResourceSerializer(
    DirectUploadUriReadOnlyMixin, serializers.HyperlinkedModelSerializer
):
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
        read_only=True, source="resource.metadata.driverShortName"
    )

    uri = serializers.CharField(read_only=True, source="resource.uri")

    class Meta:
        model = DataTable
        fields = (
            "id",
            "name",
            "title",
            "resource",
            "resource_id",
            "is_spatial",
            "driver",
            "count",
            "uri",
        )


class DataTableSerializer(DataTableListSerializer):
    class Meta(DataTableListSerializer.Meta):
        fields = DataTableListSerializer.Meta.fields + (
            "fields",
            "extent",
            "geometryFields",
            "metadata",
        )


class StorageSerializer(serializers.ModelSerializer):
    """Minimal, read-only representation of a storage a client can upload to."""

    class Meta:
        model = Storage
        fields = ("id", "name")


class ConfirmUploadRequestSerializer(serializers.Serializer):
    """Request body for ``DatasetViewSet.confirm_upload``."""

    storage = serializers.PrimaryKeyRelatedField(queryset=Storage.objects.all())
    key = serializers.CharField()
