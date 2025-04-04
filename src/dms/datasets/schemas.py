# ruff: noqa: E501
from django.db.models import TextChoices

SHARED_DEFS = {
    "person": {
        "title": "Person",
        "type": "object",
        "properties": {
            "type": {"const": "person", "widget": "hidden"},
            "last_name": {
                "type": "string",
                "title": "Last Name",
                "help_text": "Last name of the person",
            },
            "first_name": {
                "type": "string",
                "title": "First Name",
                "help_text": "First name of the person",
            },
            "email": {"type": "string", "title": "Email", "format": "email"},
            "identifier": {
                "type": "string",
                "title": "Identifier",
                "help_text": "Uniquely identifies the person when paired with an identifier type",
            },
            "affiliation": {
                "type": "string",
                "title": "Affiliation",
                "help_text": "The name of the entity affiliated, e.g. an organization's name",
            },
            "identifierScheme": {
                "type": "string",
                "title": "Identifier Type",
                "help_text": "The type of identifier that uniquely identifies the author (e.g. ORCID, ISNI)",
            },
        },
        "required": ["first_name", "last_name", "email"],
    },
    "organization": {
        "title": "Organization",
        "required": ["name", "email"],
        "type": "object",
        "properties": {
            "type": {"const": "organization", "widget": "hidden"},
            "name": {
                "type": "string",
                "title": "Name",
                "help_text": "Name of the organization",
            },
            "email": {"type": "string", "title": "Email", "format": "email"},
            "identifier": {
                "type": "string",
                "title": "Identifier",
                "help_text": "Uniquely identifies the person when paired with an identifier type",
            },
            "affiliation": {
                "type": "string",
                "title": "Affiliation",
                "help_text": "The name of the entity affiliated, e.g. an organization's name",
            },
            "identifierScheme": {
                "type": "string",
                "title": "Identifier Type",
                "help_text": "The type of identifier that uniquely identifies the author (e.g. ORCID, ISNI)",
            },
        },
    },
    "keyword": {
        "title": "Keyword",
        "help_text": "A key term that describes an important aspect of the Dataset and information about any controlled vocabulary used",
        "type": "object",
        "required": ["value", "uri"],
        "properties": {
            "value": {
                "type": "string",
                "title": "Term",
                "help_text": "A key term that describes important aspects of the Dataset",
            },
            "uri": {
                "type": "string",
                "title": "URI",
                "help_text": "A URI that points to the web presence of the Keyword Term",
                "format": "uri",
            },
            "vocabulary": {
                "type": "string",
                "title": "Controlled Vocabulary Name",
                "help_text": "The controlled vocabulary used for the keyword term (e.g. LCSH, MeSH)",
            },
            "vocabularyUri": {
                "type": "string",
                "title": "Controlled Vocabulary URL",
                "help_text": "The URL where one can access information about the term's controlled vocabulary",
                "format": "uri",
            },
        },
    },
    "topic": {
        "title": "Topic classification",
        "help_text": "Indicates a broad, important topic or subject that the Dataset covers and information about any controlled vocabulary used",
        "type": "object",
        "required": ["value", "uri"],
        "properties": {
            "value": {
                "type": "string",
                "title": "Term",
                "help_text": "A topic or subject term",
            },
            "vocabulary": {
                "type": "string",
                "title": "Controlled Vocabulary Name",
                "help_text": "The controlled vocabulary used for the keyword term (e.g. LCSH, MeSH)",
            },
            "vocabularyUri": {
                "type": "string",
                "title": "Controlled Vocabulary URL",
                "help_text": "The URL where one can access information about the term's controlled vocabulary",
                "format": "uri",
            },
        },
    },
    "publication": {
        "title": "Publication",
        "type": "object",
        "properties": {
            "relationType": {
                "type": "str",
                "help_text": "The nature of the relationship between this Dataset and the related publication",
                "enum": [],
                "title": "Relation Type",
            },
            "citation": {
                "title": "Citation",
                "type": "str",
                "help_text": "The full bibliographic citation for the related publication",
            },
            "identifierType": {
                "title": "Identifier Type",
                "type": "str",
                "enum": [],
                "help_text": "The type of identifier that uniquely identifies a related publication",
            },
            "identifier": {
                "title": "Identifier",
                "type": "str",
                "help_text": "The identifier for a related publication",
            },
            "url": {
                "title": "URL",
                "type": "str",
                "help_text": "The URL form of the identifier entered in the Identifier field, e.g. the DOI URL if a DOI was entered in the Identifier field. Used to display what was entered in the ID Type and ID Number fields as a link. If what was entered in the Identifier field has no URL form, the URL of the publication webpage is used, e.g. a journal article webpage",
            },
        },
    },
}

DATASET_METADATA_PROFILE = {
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


DATASET_METADATA_EXTERNAL_PROFILE = {
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


class DatasetProfileType(TextChoices):
    COMMON = "common", "Common"
    EXTERNAL = "external", "External"


DATASET_PROFILES = {
    DatasetProfileType.COMMON: DATASET_METADATA_PROFILE,
    DatasetProfileType.EXTERNAL: DATASET_METADATA_EXTERNAL_PROFILE,
}


class ResourceProfileType(TextChoices):
    pass


RESOURCE_PROFILES = {}
