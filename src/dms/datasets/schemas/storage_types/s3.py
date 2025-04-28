schema = {
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
