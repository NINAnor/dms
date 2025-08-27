from rest_framework.pagination import CursorPagination
from rest_framework.viewsets import ModelViewSet
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
from . import serializers


class DefaultCursorPagination(CursorPagination):
    page_size = 20
    ordering = "-id"


class DatasetViewSet(AutoPermissionViewSetMixin, ModelViewSet):
    queryset = Dataset.objects.all()
    serializer_class = serializers.DatasetSerializer
    pagination_class = DefaultCursorPagination
    filterset_class = filters.DatasetFilter

    def get_serializer_class(self):
        if self.action == "list":
            return serializers.DatasetListSerializer
        return super().get_serializer_class()


class ResourceViewSet(AutoPermissionViewSetMixin, ModelViewSet):
    queryset = Resource.objects.all()
    serializer_class = serializers.ResourceSerializer
    pagination_class = DefaultCursorPagination
    filterset_class = filters.ResourceFilter


class DatasetRelationshipViewSet(AutoPermissionViewSetMixin, ModelViewSet):
    queryset = DatasetRelationship.objects.all()
    serializer_class = serializers.DatasetRelationshipSerializer
    pagination_class = DefaultCursorPagination
    filterset_class = filters.DatasetRelationshipFilter


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
