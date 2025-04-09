# ruff: noqa: E501

schema = {
    "type": "object",
    "properties": {
        "primary_key": {
            "type": "array",
            "minItems": 1,
            "items": {"type": "string", "default": "id"},
            "title": "Primary Key",
        },
        "columns": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["name", "type"],
                "properties": {
                    "name": {
                        "type": "string",
                        "title": "Column Name",
                        "help_text": "The name of the column",
                    },
                    "type": {
                        "type": "string",
                        "title": "Column Type",
                        "help_text": "The type of the column",
                        "enum": [
                            "string",
                            "integer",
                            "float",
                            "boolean",
                            "date",
                            "datetime",
                        ],
                    },
                    "description": {
                        "type": "string",
                        "title": "Description",
                        "help_text": "A description of the column",
                        "widget": "textarea",
                    },
                    "unit": {
                        "type": "string",
                        "title": "Unit",
                        "help_text": "The unit of the column",
                    },
                    "notes": {
                        "type": "string",
                        "title": "Notes",
                        "help_text": "Additional information about the column",
                        "widget": "textarea",
                    },
                    "required": {
                        "type": "boolean",
                        "title": "Required",
                        "help_text": "Whether the column is required",
                        "default": False,
                    },
                    "unique": {
                        "type": "boolean",
                        "title": "Unique",
                        "help_text": "Whether the column values are unique",
                        "default": False,
                    },
                    "default": {
                        "type": "string",
                        "title": "Default Value",
                        "help_text": "The default value for the column",
                    },
                    "format": {
                        "type": "string",
                        "title": "Format",
                        "help_text": "The format of the column values",
                    },
                    "example": {
                        "type": "string",
                        "title": "Example Value",
                        "help_text": "An example value for the column",
                    },
                    "enum": {
                        "type": "array",
                        "items": {"type": "string"},
                        "title": "Enum Values",
                        "help_text": "The possible values for the column",
                    },
                    "skos:exactMatch": {
                        "type": "string",
                        "title": "Dictionary term URI",
                        "help_text": "A URI that points to the web presence of the Dictionary term",
                        "format": "uri",
                    },
                },
            },
        },
    },
}
