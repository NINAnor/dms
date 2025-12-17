# https://tushar.im/blog/01-drf-direct-upload-s3/

import boto3
from botocore.client import Config
from django.conf import settings

config = Config(
    signature_version="v4",
    # TODO: this is NINA specific
    s3={"addressing_style": "path"},
)
s3client = boto3.client(
    "s3",
    # TODO: this is NINA specific
    region_name="",
    endpoint_url=settings.AWS_S3_ENDPOINT_URL,
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    config=config,
)
