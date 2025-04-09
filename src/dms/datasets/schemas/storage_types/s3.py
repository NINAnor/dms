schema = {
    "type": "object",
    "properties": {
        "endpoint": {
            "type": "string",
            "title": "Endpoint",
            "help_text": "The endpoint for the S3 storage",
        },
        "bucket": {
            "type": "string",
            "title": "Bucket",
            "help_text": "The bucket for the S3 storage",
        },
        "access_key": {
            "type": "string",
            "title": "Access Key",
            "help_text": "The access key for the S3 storage",
        },
        "secret_key": {
            "type": "string",
            "title": "Secret Key",
        },
    },
    "required": ["endpoint", "bucket"],
}
