from rest_framework import serializers

from ..models import (
    Dataset,
    DatasetRelationship,
    MapResource,
    PartitionedResource,
    RasterResource,
    Resource,
    TabularResource,
)


class DatasetSerializer(serializers.HyperlinkedModelSerializer):
    project = serializers.HyperlinkedRelatedField(
        view_name="api_v1:projects-detail", read_only=True
    )
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
            "profile",
            "version",
        )


class ResourceSerializer(serializers.HyperlinkedModelSerializer):
    dataset = serializers.HyperlinkedRelatedField(
        view_name="api_v1:datasets-detail", read_only=True
    )
    url = serializers.HyperlinkedIdentityField(view_name="api_v1:resources-detail")

    class Meta:
        model = Resource
        fields = (
            "url",
            "id",
            "title",
            "name",
            "uri",
            "created_at",
            "last_modified_at",
            "dataset_id",
            "dataset",
            "metadata",
        )


class DatasetRelationshipSerializer(serializers.HyperlinkedModelSerializer):
    source = serializers.HyperlinkedRelatedField(
        view_name="api_v1:datasets-detail", read_only=True
    )
    target = serializers.HyperlinkedRelatedField(
        view_name="api_v1:datasets-detail", read_only=True
    )
    url = serializers.HyperlinkedIdentityField(
        view_name="api_v1:dataset-relationships-detail"
    )

    class Meta:
        model = DatasetRelationship
        fields = (
            "url",
            "id",
            "source",
            "source_id",
            "target",
            "target_id",
            "type",
        )


class MapResourceSerializer(serializers.HyperlinkedModelSerializer):
    dataset = serializers.HyperlinkedRelatedField(
        view_name="api_v1:datasets-detail", read_only=True
    )
    url = serializers.HyperlinkedIdentityField(view_name="api_v1:mapresources-detail")

    class Meta:
        model = MapResource
        fields = (
            "url",
            "id",
            "title",
            "uri",
            "description",
            "created_at",
            "last_modified_at",
            "dataset_id",
            "dataset",
            "metadata",
            "role",
            "access_type",
            "map_type",
        )


class RasterResourceSerializer(serializers.HyperlinkedModelSerializer):
    dataset = serializers.HyperlinkedRelatedField(
        view_name="api_v1:datasets-detail", read_only=True
    )
    url = serializers.HyperlinkedIdentityField(
        view_name="api_v1:rasterresources-detail"
    )

    class Meta:
        model = RasterResource
        fields = (
            "url",
            "id",
            "title",
            "uri",
            "description",
            "created_at",
            "last_modified_at",
            "dataset_id",
            "dataset",
            "metadata",
            "role",
            "access_type",
            "titiler",
        )


class TabularResourceSerializer(serializers.HyperlinkedModelSerializer):
    dataset = serializers.HyperlinkedRelatedField(
        view_name="api_v1:datasets-detail", read_only=True
    )
    url = serializers.HyperlinkedIdentityField(
        view_name="api_v1:tabularresources-detail"
    )

    class Meta:
        model = TabularResource
        fields = (
            "url",
            "id",
            "title",
            "name",
            "uri",
            "description",
            "created_at",
            "last_modified_at",
            "dataset_id",
            "dataset",
            "metadata",
            "role",
            "access_type",
        )


class PartitionedResourceSerializer(serializers.HyperlinkedModelSerializer):
    dataset = serializers.HyperlinkedRelatedField(
        view_name="api_v1:datasets-detail", read_only=True
    )
    url = serializers.HyperlinkedIdentityField(
        view_name="api_v1:partitionedresources-detail"
    )

    class Meta:
        model = PartitionedResource
        fields = (
            "url",
            "id",
            "title",
            "name",
            "uri",
            "description",
            "created_at",
            "last_modified_at",
            "dataset_id",
            "dataset",
            "metadata",
            "role",
            "access_type",
        )
