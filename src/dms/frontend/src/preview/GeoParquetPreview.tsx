import {
  GeoArrowPathLayer,
  GeoArrowScatterplotLayer,
  GeoArrowSolidPolygonLayer,
} from '@geoarrow/deck.gl-geoarrow';
import { readGeoParquet } from '@geoarrow/geoparquet-wasm';
import type { Layer } from '@deck.gl/core';
import { tableFromIPC, type Table } from 'apache-arrow';
import { Tab, TabGroup, TabList, TabPanel, TabPanels } from '@headlessui/react';
import wasmInit, { readParquet } from 'parquet-wasm';
import DeckGL from '@deck.gl/react';
import MaplibreMap from 'react-map-gl/maplibre';
import { useEffect, useMemo, useState } from 'react';

import 'maplibre-gl/dist/maplibre-gl.css';

import type { GdalLayer, PreviewResource } from './types';

const MAX_PREVIEW_FEATURES = 5000;
const MAX_TABLE_ROWS = 100;
const CORS_HINT =
  'Remote files must allow cross-origin requests (CORS) from this site. Check the dataset storage’s CORS configuration if the file could not be fetched.';

type GeometryKind = 'point' | 'line' | 'polygon';

function parseGeometryKind(type: string | undefined): GeometryKind | null {
  const normalized = type?.toLowerCase().replace(/[\s_-]/g, '') ?? '';
  if (normalized.includes('point')) return 'point';
  if (normalized.includes('line')) return 'line';
  if (normalized.includes('polygon')) return 'polygon';
  return null;
}

function getGeometryKind(layers: GdalLayer[] | undefined): GeometryKind | null {
  const geometryType = layers?.flatMap(layer => layer.geometryFields ?? [])[0]?.type;
  return parseGeometryKind(geometryType);
}

async function loadGeoParquet(uri: string, signal: AbortSignal): Promise<Table> {
  const response = await fetch(uri, { signal });
  if (!response.ok) {
    throw new Error(`Could not load GeoParquet (${response.status} ${response.statusText}).`);
  }

  const bytes = new Uint8Array(await response.arrayBuffer());
  try {
    const wasmTable = readGeoParquet(bytes);
    return tableFromIPC(wasmTable.intoIPCStream());
  } catch (wkbError) {
    try {
      await wasmInit();
      const wasmTable = readParquet(bytes);
      return tableFromIPC(wasmTable.intoIPCStream());
    } catch {
      throw wkbError;
    }
  }
}

function getInitialViewState(extent: PreviewResource['metadata']['wgs84Extent']) {
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
  if (coordinates.length === 0) return { longitude: 10, latitude: 72, zoom: 2 };

  const longitudes = coordinates.map(([longitude]) => longitude);
  const latitudes = coordinates.map(([, latitude]) => latitude);
  const minLongitude = Math.min(...longitudes);
  const maxLongitude = Math.max(...longitudes);
  const minLatitude = Math.min(...latitudes);
  const maxLatitude = Math.max(...latitudes);
  const span = Math.max(maxLongitude - minLongitude, (maxLatitude - minLatitude) * 2, 0.01);

  return {
    longitude: (minLongitude + maxLongitude) / 2,
    latitude: (minLatitude + maxLatitude) / 2,
    zoom: Math.max(1, Math.min(13, Math.log2(360 / span) - 1)),
  };
}

function createLayer(table: Table, geometryKind: GeometryKind): Layer {
  const data = table.slice(0, MAX_PREVIEW_FEATURES);
  const commonProps = {
    id: 'geoparquet-preview',
    data,
    pickable: true,
    autoHighlight: true,
    highlightColor: [255, 255, 0, 100],
  };

  switch (geometryKind) {
    case 'point':
      // @ts-expect-error GeoArrow layers accept Arrow Tables; upstream props type requires RecordBatch too.
      return new GeoArrowScatterplotLayer({
        ...commonProps,
        getFillColor: [30, 110, 93, 180],
        getLineColor: [20, 84, 72, 220],
        getRadius: 4,
        radiusUnits: 'pixels',
        lineWidthUnits: 'pixels',
        getLineWidth: 1,
      });
    case 'line':
      // @ts-expect-error GeoArrow layers accept Arrow Tables; upstream props type requires RecordBatch too.
      return new GeoArrowPathLayer({
        ...commonProps,
        getColor: [20, 84, 72, 220],
        getWidth: 2,
        widthUnits: 'pixels',
      });
    case 'polygon':
      // @ts-expect-error GeoArrow layers accept Arrow Tables; upstream props type requires RecordBatch too.
      return new GeoArrowSolidPolygonLayer({
        ...commonProps,
        getFillColor: [30, 110, 93, 110],
        getLineColor: [20, 84, 72, 220],
        getLineWidth: 1,
        lineWidthUnits: 'pixels',
        filled: true,
        stroked: true,
      });
  }
}

function formatCell(value: unknown, geometryType?: string): string {
  if (value === null || value === undefined) return 'NULL';
  if (geometryType) return geometryType;
  if (value instanceof Date) return value.toLocaleString();
  if (value instanceof Uint8Array) return `[binary: ${value.byteLength} bytes]`;
  if (typeof value !== 'object') return String(value);

  const formatted = JSON.stringify(value, (_, item: unknown) =>
    typeof item === 'bigint' ? item.toString() : item,
  );
  if (!formatted) return String(value);
  return formatted.length > 240 ? `${formatted.slice(0, 237)}…` : formatted;
}

function getGeometryTypes(layers: GdalLayer[] | undefined): Map<string, string> {
  return new Map(
    layers?.flatMap(
      layer =>
        layer.geometryFields?.flatMap(field =>
          field.name ? [[field.name, field.type ?? 'Geometry']] : [],
        ) ?? [],
    ) ?? [],
  );
}

export default function GeoParquetPreview({ resource }: { resource: PreviewResource }) {
  const [table, setTable] = useState<Table | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const controller = new AbortController();
    setTable(null);
    setError(null);
    setLoading(true);

    void loadGeoParquet(resource.uri, controller.signal)
      .then(setTable)
      .catch(caught => {
        if (controller.signal.aborted) return;
        setError(caught instanceof Error ? caught.message : String(caught));
      })
      .finally(() => {
        if (!controller.signal.aborted) setLoading(false);
      });

    return () => controller.abort();
  }, [resource.uri]);

  const geometryKind = useMemo(
    () => getGeometryKind(resource.metadata.layers),
    [resource.metadata.layers],
  );
  const geometryTypes = useMemo(
    () => getGeometryTypes(resource.metadata.layers),
    [resource.metadata.layers],
  );
  const tableColumns = useMemo(
    () =>
      table?.schema.fields.map(field => ({
        name: field.name,
        values: table.getChild(field.name),
        geometryType: geometryTypes.get(field.name),
      })) ?? [],
    [geometryTypes, table],
  );
  const layer = useMemo(
    () => (table && table.numRows > 0 && geometryKind ? createLayer(table, geometryKind) : null),
    [geometryKind, table],
  );

  return (
    <div
      className="preview"
      data-resource-id={resource.id}
      role="region"
      aria-label={`Preview of ${resource.title}`}
    >
      {loading && <p role="status">Loading GeoParquet…</p>}
      {error && (
        <div className="preview-error" role="alert">
          <p>{error}</p>
          <p>{CORS_HINT}</p>
        </div>
      )}
      {table && table.numRows === 0 && <p>No features found.</p>}
      {table && table.numRows > 0 && !geometryKind && (
        <p role="alert">The GeoParquet geometry type is not supported by the map preview.</p>
      )}
      {table && table.numRows > 0 && (
        <TabGroup>
          <TabList className="preview-view-tabs">
            <Tab className={({ selected }) => `btn btn-sm ${selected ? 'btn-primary' : ''}`}>
              Map
            </Tab>
            <Tab className={({ selected }) => `btn btn-sm ${selected ? 'btn-primary' : ''}`}>
              Table
            </Tab>
          </TabList>
          <TabPanels>
            <TabPanel>
              {table.numRows > MAX_PREVIEW_FEATURES && (
                <p role="status">
                  Map draws first {MAX_PREVIEW_FEATURES.toLocaleString()} of{' '}
                  {table.numRows.toLocaleString()} features. The full file is downloaded and
                  decoded.
                </p>
              )}
              {!geometryKind && (
                <p role="alert">
                  The GeoParquet geometry type is not supported by the map preview.
                </p>
              )}
              {layer && (
                <div className="geo-preview-map" aria-label="GeoParquet map preview">
                  <DeckGL
                    initialViewState={getInitialViewState(resource.metadata.wgs84Extent)}
                    controller
                    layers={[layer]}
                    style={{ position: 'relative', width: '100%', height: '100%' }}
                  >
                    <MaplibreMap mapStyle="https://tiles.openfreemap.org/styles/bright" />
                  </DeckGL>
                </div>
              )}
            </TabPanel>
            <TabPanel>
              <div className="preview-table-wrap">
                <table className="table table-zebra table-sm">
                  <thead>
                    <tr>
                      {tableColumns.map(column => (
                        <th key={column.name} scope="col" title={column.name}>
                          {column.name}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {Array.from(
                      { length: Math.min(table.numRows, MAX_TABLE_ROWS) },
                      (_, rowIndex) => (
                        <tr key={rowIndex}>
                          {tableColumns.map(column => (
                            <td key={column.name} title={column.name}>
                              {formatCell(column.values?.get(rowIndex), column.geometryType)}
                            </td>
                          ))}
                        </tr>
                      ),
                    )}
                  </tbody>
                </table>
              </div>
              {table.numRows > MAX_TABLE_ROWS && (
                <p role="status">
                  Showing first {MAX_TABLE_ROWS} of {table.numRows.toLocaleString()} rows.
                </p>
              )}
            </TabPanel>
          </TabPanels>
        </TabGroup>
      )}
    </div>
  );
}
