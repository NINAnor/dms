import abc


class StorageBase(abc.ABC):
    SCHEMA: dict = {}

    @classmethod
    @abc.abstractmethod
    def get_full_path(self, config: dict, path: str) -> str:
        return path
