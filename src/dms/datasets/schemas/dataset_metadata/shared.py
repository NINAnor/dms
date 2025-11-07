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
                "description": "Note that the personal name format should be: Last Name, First Name",
            },
            "familyName": {
                "type": "string",
                "title": "Last Name",
                "description": "Last name of the person",
            },
            "givenName": {
                "type": "string",
                "title": "First Name",
                "description": "First name of the person",
            },
            "url": {
                "type": "string",
                "description": "on-line information that can be used to contact the individual or organization",
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
                "description": "state, province of the location",
            },
            "postalcode": {"type": "string"},
            "country": {
                "type": "string",
            },
            "affiliation": {
                "type": "list",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "title": "Affiliation",
                            "description": "The name of the entity affiliated, e.g. an organization's name",
                        },
                        "affiliationIdentifier": {
                            "type": "string",
                            "title": "Uniquely identifies the organizational affiliation",
                        },
                        "affiliationIdentifierScheme": {
                            "type": "string",
                            "title": "The name of the affiliation identifier scheme",
                            "enum": ["ROR", "ISNI"],
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
                            "description": "Uniquely identifies the person when paired with an identifier type",
                        },
                        "nameIdentifierScheme": {
                            "type": "string",
                            "title": "Identifier Type",
                            "enum": IDENTIFIERS,
                            "description": "The type of identifier that uniquely identifies the author (e.g. ORCID, ISNI)",
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
