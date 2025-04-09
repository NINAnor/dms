# ruff: noqa: E501
import copy

schema = {
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

geo_schema = copy.deepcopy(schema)
geo_schema["properties"]["epsg"] = {
    "epsg": {
        "type": "integer",
        "title": "EPSG Code",
    },
    "geometry_column": {
        "type": "string",
    },
}

geo_schema["required"] = ["epsg", "geometry_column"]
