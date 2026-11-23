import { lazy, Suspense } from 'react';

import type { PreviewKind, PreviewResource } from './types';

const GeoJsonResourcePreview = lazy(() => import('./GeoJsonResourcePreview'));
const RasterPreview = lazy(() => import('./RasterPreview'));
const PMTilesPreview = lazy(() => import('./PMTilesPreview'));
const TabularPreview = lazy(() => import('./TabularPreview'));

interface AppProps {
  resource: PreviewResource;
  kind: PreviewKind;
  driver: string;
}

export default function App({ resource, kind, driver }: AppProps) {
  switch (kind) {
    case 'tabular':
      if (driver.toUpperCase() === 'GEOJSON') {
        return (
          <Suspense fallback={<p role="status">Loading GeoJSON preview…</p>}>
            <GeoJsonResourcePreview resource={resource} />
          </Suspense>
        );
      }
      if (driver.toUpperCase() === 'PMTILES') {
        return (
          <Suspense fallback={<p role="status">Loading map preview…</p>}>
            <PMTilesPreview resource={resource} />
          </Suspense>
        );
      }
      return (
        <Suspense fallback={<p role="status">Loading data preview…</p>}>
          <TabularPreview resource={resource} driver={driver} />
        </Suspense>
      );
    case 'raster':
      if (
        driver === 'GTiff' &&
        resource.metadata.metadata?.IMAGE_STRUCTURE?.LAYOUT?.toUpperCase() === 'COG'
      ) {
        return (
          <Suspense fallback={<p role="status">Loading raster preview…</p>}>
            <RasterPreview resource={resource} />
          </Suspense>
        );
      }
      return <p>Only Cloud Optimized GeoTIFFs can be previewed.</p>;
    default:
      return <p>Preview is not available for this resource type.</p>;
  }
}
