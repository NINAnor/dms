import type { FeatureCollection, GeoJsonProperties, Geometry } from 'geojson';

export interface PreviewResource {
  id: string;
  title: string;
  uri: string;
  metadata: GdalMetadata;
}

export type PreviewKind = 'tabular' | 'raster';

export type PreviewFeatureCollection = FeatureCollection<Geometry, GeoJsonProperties>;

export interface GdalMetadata {
  bands?: GdalRasterBand[];
  metadata?: {
    IMAGE_STRUCTURE?: { LAYOUT?: string };
  };
  wgs84Extent?: { coordinates?: unknown };
  layers?: GdalLayer[];
}

export interface GdalRasterBand {
  band: number;
  colorInterpretation?: string;
  minimum?: number;
  maximum?: number;
}

export interface GdalLayer {
  name: string;
  geometryFields?: Array<{
    name: string;
    coordinateSystem?: { projjson?: { id?: { authority?: string; code?: number | string } } };
  }>;
}
