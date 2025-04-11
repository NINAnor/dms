from rest_framework import serializers

from ..models import Dataset, DatasetRelationship, Resource, Storage


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
            "profile",
            "metadata",
            "fetch",
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
            "fetch",
            "version",
        )


class ResourceSerializer(serializers.HyperlinkedModelSerializer):
    dataset = serializers.HyperlinkedRelatedField(
        view_name="api_v1:datasets-detail", read_only=True
    )
    storage = serializers.HyperlinkedRelatedField(
        view_name="api_v1:storages-detail", read_only=True
    )
    url = serializers.HyperlinkedIdentityField(view_name="api_v1:resources-detail")

    class Meta:
        model = Resource
        fields = (
            "url",
            "id",
            "title",
            "name",
            "path",
            "created_at",
            "last_modified_at",
            "dataset_id",
            "dataset",
            "storage_id",
            "storage",
            "profile",
            "type",
            "schema",
            "metadata",
        )


class StorageSerializer(serializers.HyperlinkedModelSerializer):
    project = serializers.HyperlinkedRelatedField(
        view_name="api_v1:projects-detail", read_only=True
    )
    url = serializers.HyperlinkedIdentityField(view_name="api_v1:storages-detail")

    class Meta:
        model = Storage
        fields = (
            "url",
            "id",
            "title",
            "type",
            "created_at",
            "last_modified_at",
            "project",
            "project_id",
        )


class DatasetRelationshipSerializer(serializers.HyperlinkedModelSerializer):
    source = serializers.HyperlinkedRelatedField(
        view_name="api_v1:datasets-detail", read_only=True
    )
    destination = serializers.HyperlinkedRelatedField(
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
            "destination",
            "destination_id",
            "type",
        )
