import logging
import traceback
from urllib.parse import urlparse

import fsspec
import requests
import xmltodict
from bs4 import BeautifulSoup

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
        response = requests.get(f"{url}/rss", timeout=20)
        soup = BeautifulSoup(response.text, features="lxml-xml")
        datasets = []
        for item in soup.find_all("item"):
            try:
                archive = item.find("ipt:dwca")
                if archive:
                    datasets.append(
                        (
                            item.find("link").text,
                            item.find("title").text,
                            item.find("link").text.split("=")[1],
                            archive.text,
                        )
                    )
                else:
                    logger.warning(
                        f"no archive url found for {item.find('title').text}"
                    )
            except Exception:
                logger.error(traceback.format_exc())

        return datasets


class IPTResourceHarvester(DatasetUpdateHarvester):
    type = TYPE
    profile = DatasetProfileType.GBIF
    task_name = "datasets:harvest__ipt__dataset"

    def fetch(self, url):
        path = f"zip://eml.xml::{url}"
        with fsspec.open(path) as eml:
            metadata = xmltodict.parse(eml.read())
            optional = {}

            try:
                optional["title"] = metadata["eml:eml"]["dataset"]["title"]["#text"]
            except Exception:
                logger.error(traceback.format_exc())

            return metadata, optional

    def run(self, dataset):
        super().run(dataset=dataset)

        uri = urlparse(dataset.fetch["url"])
        origin = f"{uri.scheme}://{uri.netloc}"

        storage = self.get_storage(url=origin)

        Resource.objects.get_or_create(
            title="Darwin Core Archive",
            name="dwca",
            storage=storage,
            path=dataset.fetch["url"].replace(origin, ""),
            dataset=dataset,
            profile=ResourceProfileType.VECTOR,
            type=ResourceType.DWCA,
        )
