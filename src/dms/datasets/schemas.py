# ruff: noqa: E501
import copy

from django.db.models import TextChoices

CONTIBUTOR_ROLES = [
    "Data Collector",
    "Data Curator",
    "Data Manager",
    "Editor",
    "Funder",
    "Hosting Institution",
    "Project Leader",
    "Project Manager",
    "Project Member",
    "Related Person",
    "Researcher",
    "Research Group",
    "Rights Holder",
    "Sponsor",
    "Supervisor",
    "Work Package Leader",
    "Other",
]

IDENTIFIERS = [
    "ORCID",
    "ISNI",
    "LCNA",
    "VIAF",
    "GND",
    "DAI",
    "ResearcherID",
    "ScopusID",
]

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
                "enum": IDENTIFIERS,
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
                "enum": IDENTIFIERS,
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
                ],
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
    TABULAR = "tabular", "Tabular"
    VECTOR = "vector", "Vector"
    RASTER = "raster", "Raster"
    DOCUMENTATION = "documentation", "Documentation"


BASE_TABULAR_SCHEMA = {
    "type": "object",
    "properties": {
        "primary_key": {
            "type": "array",
            "minItems": 1,
            "items": {
                "type": "string",
            },
            "title": "Primary Key",
        },
        "columns": {
            "type": "array",
            "minItems": 1,
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

BASE_RASTER_SCHEMA = {
    "type": "object",
    "properties": {
        "crs": {
            "type": "integer",
            "title": "Spatial Reference System",
            "help_text": "Insert the EPSG code of the spatial reference system used",
        },
        "bands": {
            "type": "array",
            "minItems": 1,
            "items": {
                "type": "object",
                "required": ["name", "type"],
                "properties": {
                    "name": {
                        "type": "string",
                        "title": "Band Name",
                        "help_text": "The name of the band",
                    },
                    "type": {
                        "type": "string",
                        "title": "Band Type",
                        "help_text": "The type of the band",
                        "enum": [
                            "byte",
                            "int16",
                            "int32",
                            "float32",
                            "float64",
                            "uint8",
                            "uint16",
                            "uint32",
                            "int8",
                            "int64",
                        ],
                    },
                    "description": {
                        "type": "string",
                        "title": "Description",
                        "help_text": "A description of the band",
                        "widget": "textarea",
                    },
                    "unit": {
                        "type": "string",
                        "title": "Unit",
                    },
                    "minValue": {
                        "type": "number",
                    },
                    "maxValue": {
                        "type": "number",
                    },
                    "noDataValue": {
                        "type": "number",
                        "title": "No Data Value",
                    },
                    "colorMap": {
                        "type": "string",
                        "title": "Color Map",
                        "help_text": "The color map used for the band",
                    },
                },
            },
        },
    },
}

BASE_SCHEMAS = {
    ResourceProfileType.TABULAR: BASE_TABULAR_SCHEMA,
    ResourceProfileType.VECTOR: BASE_TABULAR_SCHEMA,
    ResourceProfileType.RASTER: BASE_RASTER_SCHEMA,
    ResourceProfileType.DOCUMENTATION: None,
}


class ResourceMediaType(TextChoices):
    PARQUET = "application/vnd.apache.parquet", "Parquet"
    # CSV = "text/csv", "CSV" # Should be supported?
    # JSON = "application/json", "JSON" # It's probably needed for nested/unstructured data
    COG = (
        "image/tiff; application=geotiff; profile=cloud-optimized",
        "Cloud Optimized GeoTIFF",
    )
    PDF = "application/pdf", "PDF"
    HTML = "text/html", "HTML"
    OTHER = "application/octet-stream", "Other"


PARQUET_CONFIG = {
    "type": "object",
    "properties": {
        "hive_partitioning": {
            "type": "boolean",
            "title": "Hive Partitioning",
            "help_text": "The path represents a Hive partitioned table",
        },
        "compression": {
            "type": "string",
            "title": "Compression",
            "help_text": "The compression algorithm used for the Parquet file",
            "enum": ["snappy", "gzip", "brotli"],
        },
    },
}

GEOPARQUET_CONFIG = copy.deepcopy(PARQUET_CONFIG)
GEOPARQUET_CONFIG["properties"]["epsg"] = {
    "epsg": {
        "type": "integer",
        "title": "EPSG Code",
    },
    "geometry_column": {
        "type": "string",
    },
}

GEOPARQUET_CONFIG["required"] = ["epsg", "geometry_column"]

NOTES_CONFIG = {
    "type": "object",
    "properties": {
        "notes": {
            "type": "string",
            "widget": "textarea",
        },
    },
}


RESOURCE_MEDIA_TYPE = {
    ResourceProfileType.TABULAR: {
        ResourceMediaType.PARQUET: PARQUET_CONFIG,
    },
    ResourceProfileType.VECTOR: {
        ResourceMediaType.PARQUET: GEOPARQUET_CONFIG,
    },
    ResourceProfileType.RASTER: {
        ResourceMediaType.COG: {
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
    },
    ResourceProfileType.DOCUMENTATION: {
        ResourceMediaType.HTML: NOTES_CONFIG,
        ResourceMediaType.PDF: NOTES_CONFIG,
        ResourceMediaType.OTHER: NOTES_CONFIG,
    },
}


class StorageType(TextChoices):
    HTTP = "http", "HTTP"
    S3 = "s3", "S3"


HTTP_CONFIG = {
    "type": "object",
    "properties": {
        "url": {
            "type": "string",
            "title": "URL",
            "help_text": "The Base URL to the HTTP resource",
        },
    },
}

S3_CONFIG = {
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

STORAGE_TYPE_CONFIG = {StorageType.HTTP: HTTP_CONFIG, StorageType.S3: S3_CONFIG}
