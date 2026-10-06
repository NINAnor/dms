from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.response import Response

from .serializers import PresignS3RequestSerializer


def _validation_error_detail(exc):
    """Extract a DRF-friendly detail from a Django ``ValidationError``."""
    return exc.messages if hasattr(exc, "messages") else str(exc)


def _presign_uppy_s3_request(
    storage,
    key: str,
    method: str,
    upload_id: str | None = None,
    part_number: int | None = None,
    expires_in: int = 3600,
    **context,
) -> dict:
    """Presign a single raw S3 request on behalf of a client-driven upload
    flow (e.g. Uppy's AwsS3 ``signRequest`` strategy).

    Uppy's AwsS3 plugin drives multipart orchestration itself and only needs
    a presigned URL for each raw S3 request (it POSTs/PUTs directly to S3
    with these URLs) -- the backend never calls these S3 APIs server-side.
    This lives here (rather than on ``Storage``) because it encodes Uppy's
    request shapes, not generic storage behavior.

    Dispatches on ``(method, upload_id, part_number)``, mirroring Uppy's
    ``PresignableRequest`` union:

    - ``PUT`` + ``upload_id`` + ``part_number`` -> UploadPart
    - ``PUT`` (no ``upload_id``)                -> PutObject
    - ``POST`` + ``upload_id``                  -> CompleteMultipartUpload
    - ``POST`` (no ``upload_id``)                -> CreateMultipartUpload
    - ``DELETE`` + ``upload_id``                -> AbortMultipartUpload
    - ``GET`` + ``upload_id``                   -> ListParts (resume)

    For requests that establish the object key (PutObject,
    CreateMultipartUpload), ``key`` is treated as an unrendered filename and
    the response includes the fully-rendered S3 path as ``key`` -- callers
    must use that resolved key for all subsequent requests belonging to the
    same upload. For every other request, ``key`` is expected to already be
    that resolved path.
    """
    client = storage._client()

    if method == "PUT" and upload_id and part_number:
        url = client.generate_presigned_url(
            "upload_part",
            Params={
                "Bucket": storage.bucket_name,
                "Key": key,
                "UploadId": upload_id,
                "PartNumber": part_number,
            },
            ExpiresIn=expires_in,
        )
        return {"url": url}

    if method == "PUT":
        path = storage.get_s3_path(key, **context)
        url = client.generate_presigned_url(
            "put_object",
            Params={
                "Bucket": storage.bucket_name,
                "Key": path,
                "ACL": storage.canned_acl,
            },
            ExpiresIn=expires_in,
        )
        return {"url": url, "headers": storage._acl_headers(), "key": path}

    if method == "POST" and upload_id:
        url = client.generate_presigned_url(
            "complete_multipart_upload",
            Params={"Bucket": storage.bucket_name, "Key": key, "UploadId": upload_id},
            ExpiresIn=expires_in,
        )
        return {"url": url}

    if method == "POST":
        path = storage.get_s3_path(key, **context)
        url = client.generate_presigned_url(
            "create_multipart_upload",
            Params={
                "Bucket": storage.bucket_name,
                "Key": path,
                "ACL": storage.canned_acl,
            },
            ExpiresIn=expires_in,
        )
        return {"url": url, "key": path, "headers": storage._acl_headers()}

    if method == "DELETE" and upload_id:
        url = client.generate_presigned_url(
            "abort_multipart_upload",
            Params={"Bucket": storage.bucket_name, "Key": key, "UploadId": upload_id},
            ExpiresIn=expires_in,
        )
        return {"url": url}

    if method == "GET" and upload_id:
        url = client.generate_presigned_url(
            "list_parts",
            Params={"Bucket": storage.bucket_name, "Key": key, "UploadId": upload_id},
            ExpiresIn=expires_in,
        )
        return {"url": url}

    raise ValueError(
        f"Unsupported presign request: method={method!r} "
        f"upload_id={upload_id!r} part_number={part_number!r}"
    )


class PresignedS3UploadMixin:
    """Add a single ``sign-s3-request`` endpoint that presigns a raw S3
    request on behalf of a client-driven upload flow -- e.g. Uppy's AwsS3
    plugin configured with the ``signRequest`` strategy, which calls this
    endpoint once per raw S3 API call (PutObject, CreateMultipartUpload,
    UploadPart, CompleteMultipartUpload, AbortMultipartUpload, ListParts)
    and performs that call itself using the returned presigned URL.

    Subclasses must implement ``get_presign_context(request, storage)``,
    which should validate that ``storage`` is one this request is allowed to
    upload to (raising if not) and return the server-derived context dict
    rendered into the storage's ``prefix`` template. Subclasses are also
    responsible for declaring their own permission requirements for the
    ``sign_s3_request`` action (e.g. via ``permission_type_map`` for
    ``django-rules``-based viewsets).
    """

    presign_serializer_class = PresignS3RequestSerializer

    def get_presign_context(self, request, storage):
        raise NotImplementedError

    @action(detail=True, methods=["post"], url_path="sign-s3-request")
    def sign_s3_request(self, request, pk=None):
        serializer = self.presign_serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        storage = data["storage"]

        try:
            context = self.get_presign_context(request, storage)
            result = _presign_uppy_s3_request(
                storage,
                data["key"],
                data["method"],
                upload_id=data.get("uploadId"),
                part_number=data.get("partNumber"),
                expires_in=data.get("expiresIn") or 3600,
                **context,
            )
        except (DjangoValidationError, ValueError) as exc:
            raise DRFValidationError(_validation_error_detail(exc)) from exc
        return Response(result)
