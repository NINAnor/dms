# ruff: noqa: E501

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
