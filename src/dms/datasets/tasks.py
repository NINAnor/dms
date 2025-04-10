import logging

from procrastinate.contrib.django import app

from .conf import settings
from .libs.harvesters import ipt
from .models import Dataset


@app.periodic(cron=settings.DATASETS_IPT_CRON)
@app.task(name="datasets:harvest__ipt")
def harvest_ipt_task(timestamp: int):
    harvester = ipt.IPTHarvester()
    for url in settings.DATASETS_IPT_URLS:
        logging.info(f"fetching {url}")
        harvester.run(url=url)


@app.task(name="datasets:harvest__ipt__dataset")
def harvest_ipt_dataset_task(dataset_id):
    dataset = Dataset.objects.get(id=dataset_id)
    ipt.IPTResourceHarvester().run(dataset=dataset)
