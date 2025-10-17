from rest_framework.decorators import action
from rest_framework.pagination import CursorPagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet, mixins
from rules.contrib.rest_framework import AutoPermissionViewSetMixin

from .. import filters
from ..models import (
    Dataset,
    DatasetRelationship,
    MapResource,
    PartitionedResource,
    RasterResource,
    Resource,
    TabularResource,
)
from ..schemas import dataset_metadata
from . import serializers


class DefaultCursorPagination(CursorPagination):
    page_size = 20
    ordering = "-id"


class DatasetViewSet(AutoPermissionViewSetMixin, ModelViewSet):
    queryset = Dataset.objects.all()
    serializer_class = serializers.DatasetSerializer
    pagination_class = DefaultCursorPagination
    filterset_class = filters.DatasetFilter

    permission_type_map = {
        **AutoPermissionViewSetMixin.permission_type_map,
        "metadata_schema": "view",
    }

    def get_serializer_class(self):
        if self.action == "list":
            return serializers.DatasetListSerializer
        return super().get_serializer_class()

    @action(
        detail=False,
        methods=["get"],
        url_path="metadata-schema",
        permission_classes=[AllowAny],
    )
    def metadata_schema(self, request):
        return Response(data=dataset_metadata.schema)


class ResourceViewSet(AutoPermissionViewSetMixin, ModelViewSet):
    queryset = Resource.objects.all()
    serializer_class = serializers.ResourceSerializer
    pagination_class = DefaultCursorPagination
    filterset_class = filters.ResourceFilter


class RelCursorPagination(CursorPagination):
    page_size = 200
    ordering = ["source_id", "target_id", "type"]


class DatasetRelationshipViewSet(
    AutoPermissionViewSetMixin,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    queryset = DatasetRelationship.objects.all().select_related("source", "target")
    serializer_class = serializers.DatasetRelationshipSerializer
    pagination_class = RelCursorPagination
    filterset_class = filters.DatasetRelationshipFilter
    lookup_field = "uuid"

    def get_serializer_class(self):
        if self.action == "create":
            return serializers.DatasetRelationshipCreateSerializer
        return super().get_serializer_class()

    def perform_create(self, serializer):
        if self.request.user.has_perm(
            "datasets.change_dataset", serializer.validated_data.get("source")
        ) or self.request.user.has_perm(
            "datasets.change_dataset", serializer.validated_data.get("target")
        ):
            return super().perform_create(serializer)
        raise serializers.serializers.ValidationError("You are not authorized")

    def perform_destroy(self, instance):
        if self.request.user.has_perm(
            "datasets.change_dataset", instance.source
        ) or self.request.user.has_perm("datasets.change_dataset", instance.target):
            return super().perform_destroy(instance)

        raise serializers.serializers.ValidationError("You are not authorized")


class MapResourceViewSet(AutoPermissionViewSetMixin, ModelViewSet):
    queryset = MapResource.objects.all()
    serializer_class = serializers.MapResourceSerializer
    pagination_class = DefaultCursorPagination
    filterset_class = filters.ResourceFilter


class RasterResourceViewSet(AutoPermissionViewSetMixin, ModelViewSet):
    queryset = RasterResource.objects.all()
    serializer_class = serializers.RasterResourceSerializer
    pagination_class = DefaultCursorPagination
    filterset_class = filters.ResourceFilter


class TabularResourceViewSet(AutoPermissionViewSetMixin, ModelViewSet):
    queryset = TabularResource.objects.all()
    serializer_class = serializers.TabularResourceSerializer
    pagination_class = DefaultCursorPagination
    filterset_class = filters.ResourceFilter


class PartitionedResourceViewSet(AutoPermissionViewSetMixin, ModelViewSet):
    queryset = PartitionedResource.objects.all()
    serializer_class = serializers.PartitionedResourceSerializer
    pagination_class = DefaultCursorPagination
    filterset_class = filters.ResourceFilter
