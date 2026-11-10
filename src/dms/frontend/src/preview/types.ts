export interface PreviewResource {
  id: string;
  title: string;
  uri: string;
  metadata: GdalMetadata;
}

export type PreviewKind = 'tabular' | 'raster';

export interface GdalMetadata {
  layers?: GdalLayer[];
}

export interface GdalLayer {
  name: string;
  geometryFields?: Array<{ name: string }>;
}
