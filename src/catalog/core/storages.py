from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage


class MediaRootS3Boto3Storage(S3Boto3Storage):
    location = settings.MEDIA_BASE_LOCATION
    file_overwrite = False
