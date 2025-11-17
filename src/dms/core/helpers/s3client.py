# https://tushar.im/blog/01-drf-direct-upload-s3/
import logging

import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
from django.conf import settings


class S3Client:
    """
    Docs : https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3/client/generate_presigned_post.html
    """

    def __init__(
        self,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        client_class=boto3.client,
        region_name=settings.AWS_S3_REGION_NAME,
        bucket_name=None,
    ):
        self.config = Config(
            signature_version=settings.AWS_S3_SIGNATURE_VERSION,
            s3={"addressing_style": "path"},
        )
        self.client = client_class(
            "s3",
            region_name=region_name,
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            config=self.config,
        )
        self.bucket_name = (
            bucket_name if bucket_name is not None else settings.AWS_STORAGE_BUCKET_NAME
        )

    def generate_presigned_post(self, key, expiration: int = 3600):
        try:
            response = self.client.generate_presigned_post(
                Bucket=self.bucket_name,
                Key=key,
                ExpiresIn=expiration,
            )
        except ClientError as e:
            logging.error(e)
            return None

        return response

    def generate_presigned_url(
        self, key, expiration: int = 3600, response_content_type: str = None
    ):
        params: dict = {"Bucket": self.bucket_name, "Key": key}

        if response_content_type:
            params["ResponseContentType"] = response_content_type

        try:
            response = self.client.generate_presigned_url(
                ClientMethod="get_object",
                HttpMethod="GET",
                Params=params,
                ExpiresIn=expiration,
            )
        except ClientError as e:
            logging.error(e)
            return None

        return response
