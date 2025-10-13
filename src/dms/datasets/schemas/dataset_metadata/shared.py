# ruff: noqa: E501
import copy

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
            "nameType": {
                "type": "string",
                "default": "Personal",
                "enum": ["Personal", "Organizational"],
            },
            "name": {
                "type": "string",
                "title": "Full name",
                "help_text": "Note that the personal name format should be: Last Name, First Name",
            },
            "familyName": {
                "type": "string",
                "title": "Last Name",
                "help_text": "Last name of the person",
            },
            "givenName": {
                "type": "string",
                "title": "First Name",
                "help_text": "First name of the person",
            },
            "url": {
                "type": "string",
                "help_text": "on-line information that can be used to contact the individual or organization",
            },
            "email": {"type": "string", "title": "Email", "format": "email"},
            "positionName": {
                "type": "string",
            },
            "phone": {"type": "string"},
            "address": {"type": "string"},
            "city": {"type": "string"},
            "administrativeArea": {
                "type": "string",
                "help_text": "state, province of the location",
            },
            "postalcode": {"type": "string"},
            "country": {"type": "string", "default": "Norway"},
            "affiliation": {
                "type": "list",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "title": "Affiliation",
                            "help_text": "The name of the entity affiliated, e.g. an organization's name",
                        },
                        "affiliationIdentifier": {
                            "type": "string",
                            "title": "Uniquely identifies the organizational affiliation",
                            "default": "https://isni.org/isni/000000012107519X",
                        },
                        "affiliationIdentifierScheme": {
                            "type": "string",
                            "title": "The name of the affiliation identifier scheme",
                            "enum": ["ROR", "ISNI"],
                            "default": "ISNI",
                        },
                    },
                },
            },
            "nameIdentifiers": {
                "type": "list",
                "items": {
                    "type": "object",
                    "properties": {
                        "nameIdentifier": {
                            "type": "string",
                            "title": "Identifier",
                            "help_text": "Uniquely identifies the person when paired with an identifier type",
                        },
                        "nameIdentifierScheme": {
                            "type": "string",
                            "title": "Identifier Type",
                            "enum": IDENTIFIERS,
                            "help_text": "The type of identifier that uniquely identifies the author (e.g. ORCID, ISNI)",
                        },
                    },
                },
            },
        },
        "required": [
            "name",
            "nameType",
            "email",
        ],
    },
    "geoLocationPoint": {
        "type": "object",
        "properties": {
            "pointLongitude": {"type": "number", "minimum": -180, "maximum": 180},
            "pointLatitude": {"type": "number", "minimum": -90, "maximum": 90},
        },
        "required": ["pointLongitude", "pointLatitude"],
    },
    "geoLocationBox": {
        "type": "object",
        "properties": {
            "westBoundLongitude": {"type": "number", "minimum": -180, "maximum": 180},
            "eastBoundLongitude": {"type": "number", "minimum": -180, "maximum": 180},
            "southBoundLatitude": {"type": "number", "minimum": -90, "maximum": 90},
            "northBoundLatitude": {"type": "number", "minimum": -90, "maximum": 90},
        },
        "required": [
            "westBoundLongitude",
            "eastBoundLongitude",
            "southBoundLatitude",
            "northBoundLatitude",
        ],
    },
}


SHARED_DEFS["contributor"] = copy.deepcopy(SHARED_DEFS["person"])

SHARED_DEFS["contributor"]["properties"]["contributorType"] = {
    "type": "string",
    "enum": [
        "ContactPerson",
        "DataCollector",
        "DataCurator",
        "DataManager",
        "Distributor",
        "Editor",
        "HostingInstitution",
        "Producer",
        "ProjectLeader",
        "ProjectManager",
        "ProjectMember",
        "RegistrationAgency",
        "RegistrationAuthority",
        "RelatedPerson",
        "Researcher",
        "ResearchGroup",
        "RightsHolder",
        "Sponsor",
        "Supervisor",
        "Translator",
        "WorkPackageLeader",
        "Other",
    ],
}
