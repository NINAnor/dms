from rest_framework import serializers

from buckets.models import Storage


class PresignS3RequestSerializer(serializers.Serializer):
    """Mirrors Uppy's AwsS3 ``PresignableRequest`` shape almost verbatim, so
    the frontend can forward its ``signRequest`` argument to a
    ``PresignedS3UploadMixin``-based endpoint with minimal translation."""

    storage = serializers.PrimaryKeyRelatedField(queryset=Storage.objects.all())
    key = serializers.CharField()
    method = serializers.ChoiceField(choices=["PUT", "POST", "DELETE", "GET"])
    uploadId = serializers.CharField(required=False, allow_null=True, default=None)
    partNumber = serializers.IntegerField(
        required=False, allow_null=True, default=None, min_value=1
    )
    expiresIn = serializers.IntegerField(
        required=False, allow_null=True, default=None, min_value=1
    )
