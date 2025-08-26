# ruff: noqa: E501
from .shared import SHARED_DEFS

schema = {
    "type": "object",
    "required": [
        "creators",
        "language",
    ],
    "properties": {
        "alternateIdentifiers": {
            "type": "list",
            "items": {
                "type": "object",
                "properties": {
                    "alternateIdentifier": {
                        "type": "string",
                        "title": "Value",
                        "help_text": "Another identifier uniquely identifies the Dataset",
                    },
                    "alternateIdentifierType": {
                        "type": "string",
                        "title": "Type",
                        "help_text": "The name of the agency that generated the other identifier",
                        "enum": [{"title": "DOI", "value": "DOI"}],
                    },
                },
            },
            "title": "Other Identifiers",
            "help_text": "Another unique identifier for the Dataset (e.g. producer's or another repository's identifier)",
        },
        "creators": {
            "type": "list",
            "items": SHARED_DEFS["person"],
            "minItems": 1,
            "skos:exactMatch": "http://purl.org/dc/terms/creator",
        },
        "titles": {
            "type": "list",
            "items": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                    },
                    "titleType": {
                        "type": "string",
                        "enum": [
                            "AlternativeTitle",
                            "Subtitle",
                            "TranslatedTitle",
                            "Other",
                        ],
                    },
                    "lang": {"type": "string", "enum": ["en", "no"]},
                },
                "required": ["title", "titleType"],
            },
        },
        "publicationYear": {
            "type": "number",
            "help_text": "The year when the data was or will be made publicly available",
        },
        "subjects": {
            "type": "list",
            "items": {
                "type": "object",
                "properties": {
                    "subject": {
                        "type": "string",
                    },
                    "subjectScheme": {
                        "type": "string",
                        "help_text": "The name of the subject scheme or classification code or authority if one is used",
                        "examples": [
                            "Library of Congress Subject Headings (LCSH)",
                            "ANZSRC Fields of Research",
                        ],
                    },
                    "schemeURI": {"type": "string", "format": "uri"},
                    "valueURI": {
                        "type": "string",
                        "format": "uri",
                    },
                    "classificationCode": {
                        "type": "string",
                        "help_text": "The classification code used for the subject term in the subject scheme.",
                    },
                },
            },
        },
        "contributors": {
            "type": "list",
            "items": SHARED_DEFS["contributor"],
        },
        "language": {
            "type": "string",
            "help_text": "A language that the Dataset's files is written in",
            "enum": [
                {"title": "English", "value": "en"},
                {"title": "Norsk", "value": "no"},
            ],
        },
        "related": {
            "type": "list",
            "help_text": "Relationship with external resources",
            "items": {
                "type": "object",
                "properties": {
                    "relationType": {
                        "type": "string",
                        "enum": [
                            "IsCitedBy",
                            "Cites",
                            "IsSupplementTo",
                            "IsSupplementedBy",
                            "IsContinuedBy",
                            "Continues",
                            "IsDescribedBy",
                            "Describes",
                            "HasMetadata",
                            "IsMetadataFor",
                            "HasVersion",
                            "IsVersionOf",
                            "IsNewVersionOf",
                            "IsPreviousVersionOf",
                            "IsPartOf",
                            "HasPart",
                            "IsPublishedIn",
                            "IsReferencedBy",
                            "References",
                            "IsDocumentedBy",
                            "Documents",
                            "IsCompiledBy",
                            "Compiles",
                            "IsVariantFormOf",
                            "IsOriginalFormOf",
                            "IsIdenticalTo",
                            "IsReviewedBy",
                            "Reviews",
                            "IsDerivedFrom",
                            "IsSourceOf",
                            "IsRequiredBy",
                            "Requires",
                            "IsObsoletedBy",
                            "Obsoletes",
                            "IsCollectedBy",
                            "Collects",
                            "IsTranslationOf",
                            "HasTranslation",
                        ],
                    },
                    "relatedIdentifier": {
                        "type": "string",
                    },
                    "resourceTypeGeneral": {
                        "type": "string",
                        "enum": [
                            "Audiovisual",
                            "Award",
                            "Book",
                            "BookChapter",
                            "Collection",
                            "ComputationalNotebook",
                            "ConferencePaper",
                            "ConferenceProceeding",
                            "DataPaper",
                            "Dataset",
                            "Dissertation",
                            "Event",
                            "Image",
                            "InteractiveResource",
                            "Instrument",
                            "Journal",
                            "JournalArticle",
                            "Model",
                            "OutputManagementPlan",
                            "PeerReview",
                            "PhysicalObject",
                            "Preprint",
                            "Project",
                            "Report",
                            "Service",
                            "Software",
                            "Sound",
                            "Standard",
                            "StudyRegistration",
                            "Text",
                            "Workflow",
                            "Other",
                        ],
                    },
                    "relatedIdentifierType": {
                        "type": "string",
                        "enum": [
                            "ark",
                            "arXiv",
                            "bibcode",
                            "cstr",
                            "doi",
                            "ean13",
                            "eissn",
                            "handle",
                            "isbn",
                            "issn",
                            "istc",
                            "lissn",
                            "lsid",
                            "pmid",
                            "purl",
                            "upc",
                            "url",
                            "urn",
                            "DASH-NRS",
                            "citation",
                        ],
                    },
                },
            },
        },
        "rightsList": {
            "type": "list",
            "items": {
                "type": "object",
                "properties": {
                    "rights": {"type": "string"},
                    "rightsURI": {"type": "string"},
                    "rightsIdentifier": {"type": "string"},
                    "schemeUri": {
                        "type": "string",
                        "default": "https://spdx.org/licenses/",
                    },
                },
                "required": [
                    "rights",
                ],
            },
        },
        "descriptions": {
            "type": "list",
            "items": {
                "type": "object",
                "properties": {
                    "description": {"type": "string"},
                    "descriptionType": {
                        "type": "string",
                        "enum": [
                            "Abstract",
                            "Methods",
                            "SeriesInformation",
                            "TableOfContents",
                            "TechnicalInfo",
                            "Other",
                        ],
                    },
                },
            },
        },
        "geoLocations": {
            "type": "list",
            "items": {
                "type": "object",
                "properties": {
                    "geoLocationPlace": {"type": "string"},
                },
            },
        },
    },
}
