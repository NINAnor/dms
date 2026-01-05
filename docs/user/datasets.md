# Datasets

## Concepts
A dataset can have multiple meanings depending on the context, in NINA DMS a dataset is:
> A collection of resources that are managed together and share common metadata.

A dataset is composed of one or more *resources*.

The dataset metadata is based on the DataCite schema and describes at abstract level the dataset as a whole, while each resource can have its own metadata that describes the specific resource.

Where possible some of the dataset metadata can be computed, for example:

- reference to users can be used, this avoids duplicating people information
- references to other datasets can be created in the user interface
- it's possible to automatically compute the spatial extent of the dataset based on the resources it contains

**NOTE**: it's still possible to enter register relationships to dataset/publications that are not in the system


### Resources

A resource is a reference to something and **must** provide a *uri* that describes where the data can be found and the protocol to access it.
A resource doesn't need to be accessible to be registered in the system, but it must have a meaningful *uri*.

Examples of resources with *uri* are:

- A web accessible resource: `https://path/to/the/file`
- A file: `file:///path/to/the/file`
- An S3 object: `s3://bucket-name/path/to/the/object`
- A database table: `postgresql://host:port/dbname#table_name`


Accessible resources can provide automatic metadata extraction using `GDAL`, this will allow to extract precise information about the resource like:

- Spatial extent
- Statistical information
- Data schema

Additionally some resources can provide previews, at this moment only Cloud Optimized formats are supported for previews:

- Cloud Optimized GeoTIFF (COG)
- Parquet files

#### Registering resources
It's possible to registere a resource in two ways:

- Manually, by providing the *uri* and other metadata
- Automatically, by uploading a file using the upload mechanism, this will create a resource with a file uri.

When using the upload mechainism the file will be registered as a generic resource, you can change it later to a specific type.

**NOTE**: Changes to the resource uri or change of a resource type will trigger a metadata extraction if possible.

**NOTE**: Most of these operations are performed asynchronously, so it might take some time before the metadata is available.

It's possible to update a resource previously uploaded by uploading a same resource with the same filename

### Resource Types

#### Generic Resource
A generic resource is a resource that doesn't have a specific type, it's just a reference to a *uri*.

examples:

- A PDF document stored somewhere in P: `file:///path/to/the/document.pdf`
- A web page: `https://example.com/some/page.html`
- A githhub repository

#### Map Resource
A map resource is a reference to a map product, there are two main types of map resources:

- Generic map resource: the URL of a published map (Example: an ArcGIS online map)
- A NINA map: the configuration of a NINA map (JSON document)

In both cases a preview of the map will be shown.

#### Raster Resource
A raster resource is a reference to a raster file, if the file is http-accessible the DMS will use GDAL to extact the metadata and some **approximate** statistics about the raster.

Examples of raster resources:

- A Cloud Optimized GeoTIFF (COG): `https://path/to/the/file.cog.tif`
- A GeoTIFF file stored in P: `file:///path/to/the/file.tif`
- Any other GDAL supported raster format

**NOTE**: only COG files will provide previews. Make sure to generate the COG with the appropriate overviews to have good performance.


#### Tabular Resource
A tabular resource is a reference to a tabular or vector data file, if the file is http-accessible the DMS will use GDAL to extact the metadata.

Examples of tabular resources:

- A Parquet file: `s3://bucket-name/path/to/the/file.parquet`
- A GeoPackage file stored in P: `file:///path/to/the/file.gpkg`
- Any other GDAL supported vector format

**NOTE**: Avoid Shapefiles as they represent a single resource but they are composed of multiple files.
**NOTE**: only Parquet files will provide an interactive preview.

#### Partitioned Resource
Partitioned resources are collections of files that share the same schema and represent a single logical dataset, but are composed of multiple physical files.

Examples of partitioned resources:

- A partitioned Parquet dataset stored in S3: `s3://bucket-name/path/year=2023/month=01/data.parquet`
- A hive partitioned dataset

**NOTE**: support for this resource type is not implemented yet.
