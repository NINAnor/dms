from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.pagination import CursorPagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet, mixins
from rules.contrib.rest_framework import AutoPermissionViewSetMixin

from buckets.models import Storage

from .. import filters
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
from ..schemas import dataset_metadata
from . import serializers


def _django_validation_error_detail(exc):
    """Extract a DRF-friendly detail from a Django ``ValidationError``."""
    return exc.messages if hasattr(exc, "messages") else str(exc)


class DefaultCursorPagination(CursorPagination):
    page_size = 20
    ordering = "-id"


def _upload_context(dataset, request):
    """Build the server-side context rendered into a ``Storage``'s prefix
    template. Never derived from client input."""
    context = {"dataset_id": dataset.id, "user_id": request.user.id}
    if dataset.project_id is not None:
        context["project_id"] = dataset.project_id
    return context


class DatasetViewSet(AutoPermissionViewSetMixin, ModelViewSet):
    queryset = Dataset.objects.all()
    serializer_class = serializers.DatasetSerializer
    pagination_class = DefaultCursorPagination
    filterset_class = filters.DatasetFilter

    permission_type_map = {
        **AutoPermissionViewSetMixin.permission_type_map,
        "metadata_schema": "view",
        "geojson": "view",
        "available_storages": "view",
        "upload_resource": "change",
        "sign_upload_part": "change",
        "complete_multipart_upload": "change",
        "abort_multipart_upload": "change",
        "confirm_upload": "change",
    }

    def get_serializer_class(self):
        if self.action == "list":
            return serializers.DatasetListSerializer
        if self.action == "geojson":
            return serializers.DatasetGeoSerializer
        return super().get_serializer_class()

    @action(
        detail=False,
        methods=["get"],
        url_path="metadata-schema",
        permission_classes=[AllowAny],
    )
    def metadata_schema(self, request):
        return Response(data=dataset_metadata.schema)

    @action(
        detail=True, methods=["get"], url_path="feature", url_name="geojson-feature"
    )
    def geojson(self, request, pk):
        return self.retrieve(request=request, pk=pk)

    @action(detail=True, methods=["get"], url_path="available-storages")
    def available_storages(self, request, pk=None):
        """List the storages this dataset's project may upload files to."""
        dataset = self.get_object()
        if dataset.project is None:
            storages = Storage.objects.none()
        else:
            storages = dataset.project.available_storages
        serializer = serializers.StorageSerializer(storages, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], url_path="upload-url")
    def upload_resource(self, request, pk=None):
        """Return a presigned upload URL (or multipart upload id) for a new
        resource file. This never creates a ``Resource`` row -- callers must
        confirm the upload afterwards via ``confirm_upload``."""
        dataset = self.get_object()
        serializer = serializers.UploadResourceRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            result = dataset.upload_resource(
                serializer.validated_data["storage"],
                serializer.validated_data["filename"],
                multipart=serializer.validated_data["multipart"],
                **_upload_context(dataset, request),
            )
        except DjangoValidationError as exc:
            raise DRFValidationError(_django_validation_error_detail(exc)) from exc
        return Response(result)

    @action(detail=True, methods=["post"], url_path="upload-url/sign-part")
    def sign_upload_part(self, request, pk=None):
        """Return a presigned PUT URL for a single part of a multipart upload."""
        dataset = self.get_object()
        serializer = serializers.SignUploadPartRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            result = dataset.sign_upload_part(
                data["storage"],
                data["key"],
                data["upload_id"],
                data["part_number"],
                **_upload_context(dataset, request),
            )
        except DjangoValidationError as exc:
            raise DRFValidationError(_django_validation_error_detail(exc)) from exc
        return Response(result)

    @action(detail=True, methods=["post"], url_path="upload-url/complete-multipart")
    def complete_multipart_upload(self, request, pk=None):
        """Finish a multipart upload given the collected part ETags."""
        dataset = self.get_object()
        serializer = serializers.CompleteMultipartUploadRequestSerializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            result = dataset.complete_multipart_upload(
                data["storage"],
                data["key"],
                data["upload_id"],
                data["parts"],
                **_upload_context(dataset, request),
            )
        except DjangoValidationError as exc:
            raise DRFValidationError(_django_validation_error_detail(exc)) from exc
        return Response(result)

    @action(detail=True, methods=["post"], url_path="upload-url/abort-multipart")
    def abort_multipart_upload(self, request, pk=None):
        """Abort an in-progress multipart upload."""
        dataset = self.get_object()
        serializer = serializers.AbortMultipartUploadRequestSerializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            dataset.abort_multipart_upload(
                data["storage"],
                data["key"],
                data["upload_id"],
                **_upload_context(dataset, request),
            )
        except DjangoValidationError as exc:
            raise DRFValidationError(_django_validation_error_detail(exc)) from exc
        return Response(status=204)

    @action(detail=True, methods=["post"], url_path="resources/confirm-upload")
    def confirm_upload(self, request, pk=None):
        """Client-driven callback confirming a direct-to-storage upload.

        This is *not* an S3 event notification and must not be trusted
        blindly: the backend performs a server-side ``head_object`` check
        against the storage before creating the ``Resource`` row.
        """
        dataset = self.get_object()
        serializer = serializers.ConfirmUploadRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            resource = dataset.confirm_upload(
                data["storage"], data["key"], **_upload_context(dataset, request)
            )
        except DjangoValidationError as exc:
            raise DRFValidationError(_django_validation_error_detail(exc)) from exc
        return Response(
            serializers.ResourceSerializer(
                resource, context=self.get_serializer_context()
            ).data,
            status=201,
        )


class ResourceViewSet(AutoPermissionViewSetMixin, ModelViewSet):
    queryset = Resource.objects.all()
    serializer_class = serializers.ResourceSerializer
    pagination_class = DefaultCursorPagination
    filterset_class = filters.ResourceRestFilter

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_subclasses(
                RasterResource,
                TabularResource,
            )
        )

    permission_type_map = {
        **AutoPermissionViewSetMixin.permission_type_map,
        "geojson": "view",
    }

    def get_serializer_class(self):
        if self.action == "geojson":
            return serializers.ResourceGeoSerializer
        elif self.action == "list":
            return serializers.ResourceListSerializer
        return super().get_serializer_class()

    @action(
        detail=True, methods=["get"], url_path="feature", url_name="geojson-feature"
    )
    def geojson(self, request, pk):
        return self.retrieve(request=request, pk=pk)


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


class TableCursorPagination(CursorPagination):
    page_size = 20
    ordering = ("resource", "name")


class DataTableViewSet(
    AutoPermissionViewSetMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = DataTable.objects.all().select_related("resource")
    serializer_class = serializers.DataTableSerializer
    pagination_class = TableCursorPagination
    filterset_class = filters.DataTableFilter

    def get_serializer_class(self):
        if self.action == "list":
            return serializers.DataTableListSerializer
        return super().get_serializer_class()
