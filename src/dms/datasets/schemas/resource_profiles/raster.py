# ruff: noqa: E501

schema = {
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
