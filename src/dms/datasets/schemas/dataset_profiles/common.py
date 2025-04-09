# ruff: noqa: E501
from .shared import SHARED_DEFS

schema = {
    "type": "object",
    "required": ["authors"],
    "$defs": SHARED_DEFS,
    "properties": {
        "subtitle": {
            "type": "string",
            "title": "Subtitle",
            "help_text": "A secondary title that amplifies or states certain limitations on the main title",
        },
        "alternativeTitle": {
            "type": "string",
            "title": "Alternative Title",
            "help_text": "Either 1) a title commonly used to refer to the Dataset or 2) an abbreviation of the main title",
            "skos:exactMatch": "http://purl.org/dc/terms/alternative",
        },
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
        "contacts": {
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
        "description": {
            "title": "Description",
            "type": "string",
            "widget": "textarea",
            "help_text": "A summary describing the purpose, nature, and scope of the Dataset",
        },
        "subjects": {
            "type": "array",
            "help_text": "The area of study relevant to the Dataset",
            "items": {
                "type": "string",
                "skos:exactMatch": "http://purl.org/dc/terms/subject",
                "enum": [],
            },
            "minItems": 1,
        },
        "keywords": {"type": "array", "items": {"$ref": "#/$defs/keyword"}},
        "topics": {"type": "array", "items": {"$ref": "#/$defs/topic"}},
        "publications": {"type": "array", "items": {"$ref": "#/$defs/publication"}},
        "notes": {
            "type": "string",
            "title": "Notes",
            "widget": "textarea",
            "help_text": "Additional information about the Dataset",
        },
        "language": {
            "type": "string",
            "help_text": "A language that the Dataset's files is written in",
            "enum": [
                {"title": "English", "value": "en"},
                {"title": "Norsk", "value": "no"},
            ],
        },
        "contributors": {
            "type": "list",
            "title": "Contributor",
            "help_text": "The entity, such as a person or organization, responsible for collecting, managing, or otherwise contributing to the development of the Dataset",
            "items": {
                "type": "object",
                "anyOf": [
                    SHARED_DEFS["person"],
                    SHARED_DEFS["organization"],
                ],
            },
            "minItems": 1,
            "skos:exactMatch": "http://purl.org/dc/terms/contributor",
        },
        "distibutionDate": {
            "type": "string",
            "format": "date",
            "help_text": "The date when the Dataset was made available for distribution/presentation",
        },
        "timePeriodCovered": {
            "type": "object",
            "title": "Time Period",
            "help_text": "The time period that the data refer to. Also known as span. This is the time period covered by the data, not the dates of coding, collecting data, or making documents machine-readable",
            "skos:exactMatch": "https://schema.org/temporalCoverage",
            "properties": {
                "start": {
                    "type": "string",
                    "format": "date",
                    "title": "Start",
                    "help_text": "The start date of the time period that the data refer to",
                },
                "end": {
                    "type": "string",
                    "format": "date",
                    "title": "End",
                    "help_text": "The end date of the time period that the data refer to",
                },
            },
        },
        "spatial": {
            "type": "object",
            "properties": {
                "north": {
                    "type": "number",
                    "title": "North",
                    "help_text": "The northernmost coordinate of the bounding box",
                },
                "west": {
                    "type": "number",
                    "title": "West",
                    "help_text": "The westernmost coordinate of the bounding box",
                },
                "south": {
                    "type": "number",
                    "title": "South",
                    "help_text": "The southernmost coordinate of the bounding box",
                },
                "east": {
                    "type": "number",
                    "title": "East",
                    "help_text": "The easternmost coordinate of the bounding box",
                },
            },
            "title": "Spatial Coverage",
            "help_text": "Spatial coverage of the package, expressed as bounding box coordinates",
            "skos:exactMatch": "http://purl.org/dc/terms/spatial",
        },
    },
}
