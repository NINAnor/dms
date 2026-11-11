import { lazy, Suspense } from 'react';

import TabularPreview from './TabularPreview';
import type { PreviewKind, PreviewResource } from './types';

const RasterPreview = lazy(() => import('./RasterPreview'));

interface AppProps {
  resource: PreviewResource;
  kind: PreviewKind;
  driver: string;
}

export default function App({ resource, kind, driver }: AppProps) {
  switch (kind) {
    case 'tabular':
      return <TabularPreview resource={resource} driver={driver} />;
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
