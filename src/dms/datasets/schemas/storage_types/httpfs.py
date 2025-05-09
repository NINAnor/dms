from .base import StorageBase


class HTTPFSStorage(StorageBase):
    SCHEMA = {
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "title": "URL",
                "help_text": "The Base URL to the HTTP resource",
            },
        },
    }

    @classmethod
    def get_full_path(self, config, path):
        return config["url"] + path
