# ruff: noqa: E501
from .shared import SHARED_DEFS

schema = {
    "type": "object",
    "$defs": SHARED_DEFS,
    "required": ["authors", "alternativeId"],
    "properties": {
        "alternativeId": {
            "type": "list",
            "items": {
                "type": "object",
                "properties": {
                    "value": {
                        "type": "string",
                        "title": "Value",
                        "help_text": "Another identifier uniquely identifies the Dataset",
                    },
                    "agency": {
                        "type": "string",
                        "title": "Agency",
                        "help_text": "The name of the agency that generated the other identifier",
                    },
                },
            },
            "title": "Other Identifiers",
            "help_text": "Another unique identifier for the Dataset (e.g. producer's or another repository's identifier)",
        },
        "authors": {
            "type": "list",
            "items": {
                "type": "object",
                "anyOf": [
                    SHARED_DEFS["person"],
                    SHARED_DEFS["organization"],
                ],
            },
            "minItems": 1,
            "skos:exactMatch": "http://purl.org/dc/terms/creator",
        },
        "publications": {"type": "array", "items": {"$ref": "#/$defs/publication"}},
    },
}
