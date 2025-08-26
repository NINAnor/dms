from rest_framework.pagination import CursorPagination
from rest_framework.viewsets import ReadOnlyModelViewSet

from .. import filters
from ..models import Dataset, DatasetRelationship, Resource
from . import serializers


class DefaultCursorPagination(CursorPagination):
    page_size = 20
    ordering = "-id"


class DatasetViewSet(ReadOnlyModelViewSet):
    queryset = Dataset.objects.all()
    serializer_class = serializers.DatasetSerializer
    pagination_class = DefaultCursorPagination
    filterset_class = filters.DatasetFilter

    def get_serializer_class(self):
        if self.action == "list":
            return serializers.DatasetListSerializer
        return super().get_serializer_class()


class ResourceViewSet(ReadOnlyModelViewSet):
    queryset = Resource.objects.all()
    serializer_class = serializers.ResourceSerializer
    pagination_class = DefaultCursorPagination
    filterset_class = filters.ResourceFilter


class DatasetRelationshipViewSet(ReadOnlyModelViewSet):
    queryset = DatasetRelationship.objects.all()
    serializer_class = serializers.DatasetRelationshipSerializer
    pagination_class = DefaultCursorPagination
    # filterset_class = filters.ResourceFilter
