import pyarrow as pa
import pyarrow.parquet as pq
import s3fs

from ...conf import settings
from ...models import Dataset

PROFILE_FACTORY = {}


def to_records():
    datasets = Dataset.objects.all()
    rows = []

    for ds in datasets:
        factory = PROFILE_FACTORY.get(ds.profile)

        if not factory:
            continue

        row = factory.build(ds)
        rows.append(row.model_dump())

    print("converting to arrow")
    records = pa.Table.from_pylist(rows)
    s3 = s3fs.S3FileSystem(
        key=settings.AWS_ACCESS_KEY_ID,
        secret=settings.AWS_SECRET_ACCESS_KEY,
        endpoint_url=settings.AWS_S3_ENDPOINT_URL,
        config_kwargs={"signature_version": settings.AWS_S3_SIGNATURE_VERSION},
    )
    with s3.open(
        f"s3://{settings.AWS_STORAGE_BUCKET_NAME}{settings.DATASETS_CSW_PARQUET_PATH}.parquet",
        "wb",
    ) as f:
        print("write to s3")
        pq.write_table(records, f)
