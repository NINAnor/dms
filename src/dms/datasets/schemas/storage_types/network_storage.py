from .base import StorageBase


class NetworkStorage(StorageBase):
    SCHEMA = {
        "type": "object",
        "properties": {
            "base_path": {
                "type": "string",
                "title": "Base Path",
                "help_text": "The path that should be used as a prefix to every resource",  # noqa: E501
            },
        },
        "required": ["base_path"],
    }

    @classmethod
    def get_full_path(self, config, path):
        return config["base_path"] + path
