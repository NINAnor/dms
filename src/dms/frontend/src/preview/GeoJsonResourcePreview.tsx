import { lazy, Suspense, useEffect, useState } from 'react';

import type { Feature, Geometry } from 'geojson';

import type { PreviewFeatureCollection, PreviewResource } from './types';

const GeoJsonPreview = lazy(() => import('./GeoJsonPreview'));

const CORS_HINT =
  'Remote files must allow cross-origin requests (CORS) from this site. Check the dataset storage’s CORS configuration if the file could not be fetched.';

function toFeatureCollection(value: unknown): PreviewFeatureCollection {
  if (!value || typeof value !== 'object' || !('type' in value)) {
    throw new Error('The resource does not contain valid GeoJSON.');
  }

  const geoJson = value as { type: unknown; features?: unknown };
  if (geoJson.type === 'FeatureCollection' && Array.isArray(geoJson.features)) {
    return value as PreviewFeatureCollection;
  }
  if (geoJson.type === 'Feature') {
    return { type: 'FeatureCollection', features: [value as Feature] };
  }
  if (
    ['Point', 'MultiPoint', 'LineString', 'MultiLineString', 'Polygon', 'MultiPolygon'].includes(
      String(geoJson.type),
    ) ||
    geoJson.type === 'GeometryCollection'
  ) {
    return {
      type: 'FeatureCollection',
      features: [{ type: 'Feature', geometry: value as Geometry, properties: {} }],
    };
  }

  throw new Error('The resource does not contain valid GeoJSON.');
}

export default function GeoJsonResourcePreview({ resource }: { resource: PreviewResource }) {
  const [data, setData] = useState<PreviewFeatureCollection | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const controller = new AbortController();
    setData(null);
    setError(null);
    setLoading(true);

    void fetch(resource.uri, { signal: controller.signal })
      .then(async response => {
        if (!response.ok) {
          throw new Error(`Could not load GeoJSON (${response.status} ${response.statusText}).`);
        }
        return toFeatureCollection(await response.json());
      })
      .then(setData)
      .catch(caught => {
        if (controller.signal.aborted) return;
        setError(caught instanceof Error ? caught.message : String(caught));
      })
      .finally(() => {
        if (!controller.signal.aborted) setLoading(false);
      });

    return () => controller.abort();
  }, [resource.uri]);

  return (
    <div
      className="preview"
      data-resource-id={resource.id}
      role="region"
      aria-label={`Preview of ${resource.title}`}
    >
      {loading && <p role="status">Loading GeoJSON…</p>}
      {error && (
        <div className="preview-error" role="alert">
          <p>{error}</p>
          <p>{CORS_HINT}</p>
        </div>
      )}
      {data && data.features.length === 0 && <p>No features found.</p>}
      {data && data.features.length > 0 && (
        <Suspense fallback={<p role="status">Loading map renderer…</p>}>
          <GeoJsonPreview data={data} />
        </Suspense>
      )}
    </div>
  );
}
