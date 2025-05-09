from datetime import date

from pydantic import BaseModel

from ...models import Dataset


class CSWMetadata(BaseModel):
    identifier: str
    typename: str = "gmd:MD_Metadata"
    schema: str = "http://www.isotc211.org/2005/gmd"
    mdsource: str = "local"
    insert_date: date
    title: str
    date_modified: date
    type: str = "service"
    format: str | None = None
    wkt_geometry: str
    metadata: str
    xml: str
    keywords: str
    metadata_type: str = "application/xml"
    anytext: str
    abstract: str | None = None
    date: date
    creator: str | None = None
    publisher: str | None = None
    contributor: str | None = None
    links: str | None = None


class BaseFactory:
    def build(dataset: Dataset) -> CSWMetadata:
        raise NotImplementedError()
