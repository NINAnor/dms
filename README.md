# NINA Data Management System (DMS)

The NINA Data Management System (DMS) is a comprehensive Django-based web application which manages research data and projects at NINA. The system provides:

- **Project Management**: Create and manage research projects with team memberships and roles
- **Dataset Management**: Catalog, store, and manage research datasets with metadata
- **Data Management Plans (DMPs)**: Create and manage data management plans using configurable surveys
- **Storage Integration**: Connect to various storage backends (S3, Zenodo, IPT, GBIF)
- **API Access**: RestAPI for access to all resources
- **Geospatial Support**: Built-in support for geographic datasets using PostGIS

The system integrates with external services like LDAP for authentication, S3-compatible storage for data files.


## How to setup
Check the [development setup instructions](docs/dev/setup.md) for details on how to get started with development.
