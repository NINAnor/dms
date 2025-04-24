from datetime import datetime
from urllib.parse import urlparse

from dms.datasets.models import Dataset, Storage
from dms.datasets.schemas.storage_types import StorageType


class BaseHarvester:
    type = None
    profile = None
    task_name = None

    def get_storage(self, url: str):
        uri = urlparse(url)
        storage, _ = Storage.objects.get_or_create(
            title=uri.netloc, type=StorageType.HTTP, defaults={"config": {"url": url}}
        )
        return storage

    def fetch(self, url: str):
        raise NotImplementedError()

    def run(self):
        raise NotImplementedError()

    def get_dataset(self, dataset_id: str) -> Dataset | None:
        return Dataset.objects.filter(fetch__id=dataset_id).first()

    def get_or_create_dataset(
        self, dataset_id: str, name: str, slug: str, url: str
    ) -> Dataset:
        ds = self.get_dataset(dataset_id=dataset_id)
        fetch_data = {
            "id": dataset_id,
            "type": self.type,
            "last_fetch": datetime.now(),
            "url": url,
            "task_name": self.task_name,
        }
        if not ds:
            ds = Dataset.objects.create(
                profile=self.profile,
                title=name,
                name=slug,
                fetch=fetch_data,
            )
        else:
            ds.fetch = fetch_data
            ds.save()

        return ds

    def update_dataset(
        self, dataset: Dataset, metadata: dict, optional: dict = None
    ) -> None:
        if optional is not None:
            for key, value in optional.items():
                setattr(dataset, key, value)

        dataset.metadata = metadata
        dataset.fetch["last_fetch"] = datetime.now()
        dataset.save()


class DatasetListHarvester(BaseHarvester):
    def fetch(self, url: str) -> list[tuple[str, str, str, str]]:
        raise NotImplementedError()

    def run(self, url: str):
        datasets = self.fetch(url)
        for dataset_id, name, slug, url in datasets:
            self.get_or_create_dataset(
                dataset_id=dataset_id, name=name, url=url, slug=slug
            )

    def get_or_create_dataset(
        self, dataset_id: str, name: str, slug: str, url: str
    ) -> Dataset:
        dataset = super().get_or_create_dataset(
            dataset_id=dataset_id, name=name, slug=slug, url=url
        )
        dataset.fetch_updates()
        return dataset


class DatasetUpdateHarvester(BaseHarvester):
    def fetch(self, url: str) -> tuple[dict, dict]:
        raise NotImplementedError()

    def run(self, dataset: Dataset):
        metadata, optional = self.fetch(dataset.fetch["url"])
        self.update_dataset(dataset=dataset, metadata=metadata, optional=optional)
