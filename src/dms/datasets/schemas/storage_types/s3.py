from .base import StorageBase


class SimpleObjectStorage(StorageBase):
    SCHEMA = {
        "type": "object",
        "properties": {
            "endpoint": {
                "type": "string",
                "title": "Endpoint",
                "help_text": "The endpoint for the S3 storage",
            },
            "url_style": {"type": "string", "enum": ["vhost", "path"]},
        },
        "required": ["endpoint", "url_style"],
    }

    @classmethod
    def get_full_path(self, config, path):
        return f"s3://{path}?s3_endpoint={config['endpoint']}&s3_url_style={config['url_style']}"
