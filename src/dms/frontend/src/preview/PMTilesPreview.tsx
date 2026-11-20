import maplibregl from 'maplibre-gl';
import { PMTiles, Protocol } from 'pmtiles';
import { useEffect, useRef, useState } from 'react';

import 'maplibre-gl/dist/maplibre-gl.css';

import type { GdalLayer, PreviewResource } from './types';

const GEOMETRY_KINDS = ['points', 'lines', 'polygons'] as const;
type GeometryKind = (typeof GEOMETRY_KINDS)[number];

interface PMTilesVectorLayer {
  name: string;
  geometryKinds: GeometryKind[];
  userSelectable: boolean;
}

const pmtilesProtocol = new Protocol({ metadata: false });
maplibregl.addProtocol('pmtiles', pmtilesProtocol.tile);

function parseGeometryKind(type: string | undefined): GeometryKind | null {
  const normalized = type?.toLowerCase().replace(/[\s_-]/g, '') ?? '';
  if (normalized.includes('point')) return 'points';
  if (normalized.includes('line')) return 'lines';
  if (normalized.includes('polygon')) return 'polygons';
  return null;
}

function getResourceVectorLayers(layers: GdalLayer[] | undefined): PMTilesVectorLayer[] {
  return (
    layers?.map(layer => {
      const fieldTypes = layer.geometryFields?.map(field => parseGeometryKind(field.type)) ?? [];
      const userSelectable = fieldTypes.length === 0 || fieldTypes.some(type => type === null);
      const geometryKinds = userSelectable
        ? [...GEOMETRY_KINDS]
        : [...new Set(fieldTypes.filter((type): type is GeometryKind => type !== null))];

      return { name: layer.name, geometryKinds, userSelectable };
    }) ?? []
  );
}

function getVectorLayersFromPMTiles(metadata: unknown): PMTilesVectorLayer[] {
  if (!metadata || typeof metadata !== 'object' || !('vector_layers' in metadata)) return [];

  const vectorLayers = (metadata as { vector_layers?: unknown }).vector_layers;
  if (!Array.isArray(vectorLayers)) return [];

  return vectorLayers.flatMap(layer => {
    if (!layer || typeof layer !== 'object' || !('id' in layer)) return [];
    if (typeof layer.id !== 'string') return [];

    const type =
      'geometry_type' in layer && typeof layer.geometry_type === 'string'
        ? parseGeometryKind(layer.geometry_type)
        : null;

    return [
      {
        name: layer.id,
        geometryKinds: type ? [type] : [...GEOMETRY_KINDS],
        userSelectable: type === null,
      },
    ];
  });
}

function getWgs84Bounds(
  extent: PreviewResource['metadata']['wgs84Extent'],
): [[number, number], [number, number]] | null {
  const coordinates: Array<[number, number]> = [];

  function collect(value: unknown) {
    if (!Array.isArray(value)) return;
    if (typeof value[0] === 'number' && typeof value[1] === 'number') {
      coordinates.push([value[0], value[1]]);
      return;
    }
    value.forEach(collect);
  }

  collect(extent?.coordinates);
  if (coordinates.length === 0) return null;

  const longitudes = coordinates.map(([longitude]) => longitude);
  const latitudes = coordinates.map(([, latitude]) => latitude);
  return [
    [Math.min(...longitudes), Math.min(...latitudes)],
    [Math.max(...longitudes), Math.max(...latitudes)],
  ];
}

export default function PMTilesPreview({ resource }: { resource: PreviewResource }) {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<maplibregl.Map | null>(null);
  const sourceLayersRef = useRef<PMTilesVectorLayer[]>([]);
  const [mapReady, setMapReady] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [vectorLayers, setVectorLayers] = useState<PMTilesVectorLayer[]>([]);
  const [geometryTypes, setGeometryTypes] = useState({
    points: true,
    lines: true,
    polygons: true,
  });
  const geometryTypesRef = useRef(geometryTypes);
  geometryTypesRef.current = geometryTypes;

  useEffect(() => {
    const containerElement = mapContainerRef.current;
    if (!containerElement) return;
    const container: HTMLDivElement = containerElement;

    let cancelled = false;
    let map: maplibregl.Map | undefined;
    let observer: ResizeObserver | undefined;
    setMapReady(false);
    setLoading(true);
    setError(null);
    setVectorLayers([]);
    sourceLayersRef.current = [];
    const defaultGeometryTypes = { points: true, lines: true, polygons: true };
    geometryTypesRef.current = defaultGeometryTypes;
    setGeometryTypes(defaultGeometryTypes);

    async function initialize() {
      try {
        const archiveUrl = resource.uri.startsWith('pmtiles://')
          ? resource.uri.slice('pmtiles://'.length)
          : resource.uri;
        const archive = new PMTiles(archiveUrl);
        pmtilesProtocol.add(archive);

        let layers = getResourceVectorLayers(resource.metadata.layers);
        if (layers.length === 0) {
          layers = getVectorLayersFromPMTiles(await archive.getMetadata());
        }
        if (cancelled) return;
        if (layers.length === 0) throw new Error('No vector layers found in this PMTiles archive.');
        sourceLayersRef.current = layers;
        setVectorLayers(layers);

        const activeMap = new maplibregl.Map({
          container,
          style: 'https://tiles.openfreemap.org/styles/bright',
          center: [10, 72],
          zoom: 2,
        });
        map = activeMap;
        activeMap.addControl(new maplibregl.NavigationControl(), 'top-right');
        activeMap.addControl(new maplibregl.ScaleControl({ maxWidth: 80, unit: 'metric' }));
        mapRef.current = activeMap;

        activeMap.once('load', () => {
          if (cancelled) return;
          try {
            activeMap.addSource('pmtiles-preview', {
              type: 'vector',
              url: `pmtiles://${archiveUrl}`,
            });

            layers.forEach((sourceLayer, index) => {
              if (sourceLayer.geometryKinds.includes('polygons')) {
                activeMap.addLayer({
                  id: `pmtiles-preview-fill-${index}`,
                  type: 'fill',
                  source: 'pmtiles-preview',
                  'source-layer': sourceLayer.name,
                  filter: ['==', '$type', 'Polygon'],
                  layout: {
                    visibility:
                      sourceLayer.userSelectable && !geometryTypesRef.current.polygons
                        ? 'none'
                        : 'visible',
                  },
                  paint: {
                    'fill-color': '#1e6e5d',
                    'fill-opacity': 0.3,
                    'fill-outline-color': '#145448',
                  },
                });
              }
              if (sourceLayer.geometryKinds.includes('lines')) {
                activeMap.addLayer({
                  id: `pmtiles-preview-line-${index}`,
                  type: 'line',
                  source: 'pmtiles-preview',
                  'source-layer': sourceLayer.name,
                  filter: ['==', '$type', 'LineString'],
                  layout: {
                    visibility:
                      sourceLayer.userSelectable && !geometryTypesRef.current.lines
                        ? 'none'
                        : 'visible',
                  },
                  paint: { 'line-color': '#145448', 'line-width': 1.5 },
                });
              }
              if (sourceLayer.geometryKinds.includes('points')) {
                activeMap.addLayer({
                  id: `pmtiles-preview-point-${index}`,
                  type: 'circle',
                  source: 'pmtiles-preview',
                  'source-layer': sourceLayer.name,
                  filter: ['==', '$type', 'Point'],
                  layout: {
                    visibility:
                      sourceLayer.userSelectable && !geometryTypesRef.current.points
                        ? 'none'
                        : 'visible',
                  },
                  paint: {
                    'circle-radius': 4,
                    'circle-color': '#1e6e5d',
                    'circle-stroke-color': '#145448',
                    'circle-stroke-width': 1,
                  },
                });
              }
            });

            const bounds = getWgs84Bounds(resource.metadata.wgs84Extent);
            if (bounds) activeMap.fitBounds(bounds, { padding: 24 });
            setMapReady(true);
            setLoading(false);
          } catch (caught) {
            setError(caught instanceof Error ? caught.message : String(caught));
            setLoading(false);
          }
        });

        activeMap.on('error', event => {
          if (!cancelled && event.error) {
            setError(event.error.message);
            setLoading(false);
          }
        });

        if (typeof ResizeObserver !== 'undefined') {
          observer = new ResizeObserver(() => activeMap.resize());
          observer.observe(container);
        }
      } catch (caught) {
        if (!cancelled) {
          setError(caught instanceof Error ? caught.message : String(caught));
          setLoading(false);
        }
      }
    }

    void initialize();

    return () => {
      cancelled = true;
      observer?.disconnect();
      mapRef.current = null;
      map?.remove();
    };
  }, [resource.id, resource.metadata.layers, resource.metadata.wgs84Extent, resource.uri]);

  useEffect(() => {
    const map = mapRef.current;
    if (!map || !mapReady) return;

    sourceLayersRef.current.forEach((sourceLayer, index) => {
      if (!sourceLayer.userSelectable) return;
      if (sourceLayer.geometryKinds.includes('polygons')) {
        map.setLayoutProperty(
          `pmtiles-preview-fill-${index}`,
          'visibility',
          geometryTypes.polygons ? 'visible' : 'none',
        );
      }
      if (sourceLayer.geometryKinds.includes('lines')) {
        map.setLayoutProperty(
          `pmtiles-preview-line-${index}`,
          'visibility',
          geometryTypes.lines ? 'visible' : 'none',
        );
      }
      if (sourceLayer.geometryKinds.includes('points')) {
        map.setLayoutProperty(
          `pmtiles-preview-point-${index}`,
          'visibility',
          geometryTypes.points ? 'visible' : 'none',
        );
      }
    });
  }, [geometryTypes, mapReady]);

  return (
    <div className="pmtiles-preview" aria-label={`PMTiles map preview of ${resource.title}`}>
      {vectorLayers.some(layer => layer.userSelectable) && (
        <div className="pmtiles-preview-controls" role="group" aria-label="Render geometry">
          <label className="label cursor-pointer gap-2">
            <input
              className="checkbox checkbox-sm"
              type="checkbox"
              checked={geometryTypes.points}
              onChange={event =>
                setGeometryTypes(current => ({ ...current, points: event.target.checked }))
              }
            />
            <span className="label-text">Points</span>
          </label>
          <label className="label cursor-pointer gap-2">
            <input
              className="checkbox checkbox-sm"
              type="checkbox"
              checked={geometryTypes.lines}
              onChange={event =>
                setGeometryTypes(current => ({ ...current, lines: event.target.checked }))
              }
            />
            <span className="label-text">Lines</span>
          </label>
          <label className="label cursor-pointer gap-2">
            <input
              className="checkbox checkbox-sm"
              type="checkbox"
              checked={geometryTypes.polygons}
              onChange={event =>
                setGeometryTypes(current => ({ ...current, polygons: event.target.checked }))
              }
            />
            <span className="label-text">Polygons</span>
          </label>
        </div>
      )}
      {loading && <p role="status">Loading PMTiles map preview…</p>}
      {error && (
        <div className="preview-error" role="alert">
          <p>{error}</p>
          <p>PMTiles sources must allow cross-origin byte-range requests.</p>
        </div>
      )}
      <div ref={mapContainerRef} className="geo-preview-map" />
    </div>
  );
}
