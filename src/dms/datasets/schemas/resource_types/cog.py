schema = {
    "type": "object",
    "properties": {
        "epsg": {
            "type": "integer",
            "title": "EPSG Code",
        },
        "notes": {
            "type": "string",
            "widget": "textarea",
        },
    },
    "required": ["epsg"],
}
