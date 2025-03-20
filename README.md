# NINA Data Management System (DMS)


## Requirements
- Docker
- Nix (optional)
- Direnv (optional)

## How to setup
```bash
cp .env.example .env
# fill .env with values that make sense
docker compose --profile dev up -d --build
```

## Structure
```mermaid
mindmap
  root((NINA DMS))
    Projects
      UBW
      DMP
    Datasets
      dms
      Metadata
      DOI
      Sharing
        GBIF
        GeoNorge
        Zenodo
    Maps
        internal
        public
```
