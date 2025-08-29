# NINA Data Management System (DMS)


## Requirements
- Docker
- uv

## How to setup
```bash
cp .env.example .env
# fill .env with values that make sense
source .helpers
dpcli_dev up -d
```

## Structure
```mermaid
mindmap
  root((NINA DMS))
    Projects
      UBW
      DMP
    Datasets
      Catalog
      Metadata
      DOI
      Sharing
        GBIF
        GeoNorge
      Storage
        Zenodo
        IPT
        NINA S3
    Maps
        Internal
        Public
```
