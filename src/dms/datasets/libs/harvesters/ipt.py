import logging
import traceback
from urllib.parse import urlparse

import requests

from dms.datasets.models import Resource
from dms.datasets.schemas.dataset_profiles import DatasetProfileType
from dms.datasets.schemas.resource_profiles import ResourceProfileType
from dms.datasets.schemas.resource_types import ResourceType

from .harvester import DatasetListHarvester, DatasetUpdateHarvester

logger = logging.getLogger(__name__)

TYPE = "IPT"


class IPTHarvester(DatasetListHarvester):
    type = TYPE
    profile = DatasetProfileType.GBIF
    task_name = "datasets:harvest__ipt__dataset"

    def fetch(self, url):
        self.get_storage(url=url)
        response = requests.get(url, timeout=20)
        resources = response.json()["resources"]
        datasets = []
        for item in resources:
            try:
                datasets.append(
                    (
                        item.get("link"),
                        item.get("title"),
                        item.get("id"),
                        item.get("url"),
                    )
                )
            except Exception:
                logger.error(traceback.format_exc())

        return datasets


class IPTResourceHarvester(DatasetUpdateHarvester):
    type = TYPE
    profile = DatasetProfileType.GBIF
    task_name = "datasets:harvest__ipt__dataset"

    def fetch(self, url):
        response = requests.get(url, timeout=20)
        resource = response.json()
        self.context["resource"] = resource
        return resource.get("meta"), {
            "title": resource["meta"]["eml:eml"]["dataset"]["title"]["#text"]
        }

    def run(self, dataset):
        super().run(dataset=dataset)

        uri = urlparse(self.context["resource"]["ipt_dwca"])

        storage = self.get_storage(url=f"{uri.scheme}://{uri.netloc}")

        Resource.objects.get_or_create(
            title="Darwin Core Archive",
            name="dwca",
            storage=storage,
            path=f"{uri.path}?{uri.query}" if uri.query else uri.path,
            dataset=dataset,
            profile=ResourceProfileType.VECTOR,
            type=ResourceType.DWCA,
        )

        uri = urlparse(self.context["resource"]["parquet_url"])
        storage = self.get_storage(url=f"{uri.scheme}://{uri.netloc}")

        Resource.objects.get_or_create(
            title="Parquet",
            name="parquet",
            storage=storage,
            path=f"{uri.path}?{uri.query}" if uri.query else uri.path,
            dataset=dataset,
            profile=ResourceProfileType.VECTOR,
            type=ResourceType.PARQUET,
        )
