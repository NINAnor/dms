import * as duckdb from '@duckdb/duckdb-wasm';
import {
  flexRender,
  getCoreRowModel,
  useReactTable,
  type ColumnDef,
  type ColumnSizingState,
} from '@tanstack/react-table';
import { useVirtualizer } from '@tanstack/react-virtual';
import { lazy, Suspense, useEffect, useRef, useState, type RefObject } from 'react';

import duckdbMvpWasm from '@duckdb/duckdb-wasm/dist/duckdb-mvp.wasm?url';
import duckdbMvpWorker from '@duckdb/duckdb-wasm/dist/duckdb-browser-mvp.worker.js?url';
import duckdbEhWasm from '@duckdb/duckdb-wasm/dist/duckdb-eh.wasm?url';
import duckdbEhWorker from '@duckdb/duckdb-wasm/dist/duckdb-browser-eh.worker.js?url';

import type { PreviewFeatureCollection, PreviewResource } from './types';

const GeoJsonPreview = lazy(() => import('./GeoJsonPreview'));

const ROWS_PER_PAGE = 100;
const DEFAULT_MAP_FEATURE_LIMIT = 5000;
const GEOJSON_COLUMN = '__preview_geometry';

const bundles: duckdb.DuckDBBundles = {
  mvp: {
    mainModule: new URL(duckdbMvpWasm, import.meta.url).toString(),
    mainWorker: new URL(duckdbMvpWorker, import.meta.url).toString(),
  },
  eh: {
    mainModule: new URL(duckdbEhWasm, import.meta.url).toString(),
    mainWorker: new URL(duckdbEhWorker, import.meta.url).toString(),
  },
};

type PreviewRow = Record<string, unknown>;

interface QueryResult {
  columns: string[];
  geometryColumns: string[];
  rows: PreviewRow[];
  hasMore: boolean;
}

interface PreviewBatch {
  schema: { fields: Array<{ name: string }> };
  toArray: () => Array<{ toJSON: () => PreviewRow }>;
}

interface PreviewError {
  message: string;
  hint?: string;
}

const CORS_HINT =
  'Remote files must allow cross-origin requests (CORS) from this site. Check the dataset storage’s CORS configuration if the file could not be fetched.';

class UnsupportedGdalDriverError extends Error {}

function toPreviewError(caught: unknown): PreviewError {
  return {
    message: caught instanceof Error ? caught.message : String(caught),
    hint: caught instanceof UnsupportedGdalDriverError ? undefined : CORS_HINT,
  };
}

function useVisible(ref: RefObject<HTMLElement | null>) {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const element = ref.current;
    if (!element) return;

    if (!('IntersectionObserver' in window)) {
      setVisible(true);
      return;
    }

    const observer = new IntersectionObserver(([entry]) => {
      if (entry?.isIntersecting) {
        setVisible(true);
        observer.disconnect();
      }
    });

    observer.observe(element);
    return () => observer.disconnect();
  }, [ref]);

  return visible;
}

async function executePreview(
  connection: duckdb.AsyncDuckDBConnection,
  resource: PreviewResource,
  driver: string,
  layerIndex: number,
): Promise<{ previewQuery: string; geometryColumns: string[]; source: string }> {
  const layer = resource.metadata.layers?.[layerIndex] ?? resource.metadata.layers?.[0];
  const geometryColumns = [
    ...new Set(layer?.geometryFields?.map(field => field.name).filter(Boolean) ?? []),
  ];
  const quoteIdentifier = (identifier: string) => `"${identifier.replace(/"/g, '""')}"`;
  const quoteLiteral = (value: string) => `'${value.replace(/'/g, "''")}'`;
  const geometryReplacements = geometryColumns
    .map(name => {
      const quotedName = quoteIdentifier(name);
      return `ST_AsText(${quotedName}) AS ${quotedName}`;
    })
    .join(', ');
  const quotedUri = quoteLiteral(resource.uri);

  await connection.query('INSTALL httpfs');
  await connection.query('LOAD httpfs');
  const isParquet = driver.toLowerCase() === 'parquet';
  if (!isParquet || geometryColumns.length > 0) {
    await connection.query('INSTALL spatial');
    await connection.query('LOAD spatial');
  }

  let source: string;
  if (isParquet) {
    source = `read_parquet(${quotedUri})`;
  } else {
    const drivers = await connection.query('SELECT short_name FROM ST_Drivers() WHERE can_open');
    const supported = drivers.toArray().some(row => {
      const shortName = row.toJSON().short_name;
      return typeof shortName === 'string' && shortName.toUpperCase() === driver.toUpperCase();
    });
    if (!supported) {
      throw new UnsupportedGdalDriverError(
        `DuckDB Spatial does not support the GDAL driver “${driver}”.`,
      );
    }
    source = `ST_Read(${quotedUri}, layer := ${quoteLiteral(layer?.name ?? '')})`;
  }

  const previewQuery = `SELECT *${geometryReplacements ? ` REPLACE (${geometryReplacements})` : ''} FROM ${source}`;
  return { previewQuery, geometryColumns, source };
}

async function readGeoJsonPreview(
  connection: duckdb.AsyncDuckDBConnection,
  source: string,
  geometryColumn: string,
  sourceCrs?: string,
  featureLimit = DEFAULT_MAP_FEATURE_LIMIT,
): Promise<PreviewFeatureCollection> {
  const quotedColumn = `"${geometryColumn.replace(/"/g, '""')}"`;
  const geometryExpression =
    sourceCrs && sourceCrs !== 'OGC:CRS84'
      ? `ST_Transform(${quotedColumn}, '${sourceCrs.replace(/'/g, "''")}', 'EPSG:4326', always_xy := true)`
      : quotedColumn;
  const result = await connection.query(
    `SELECT ST_AsGeoJSON(${geometryExpression}) AS "${GEOJSON_COLUMN}" FROM ${source} WHERE ${quotedColumn} IS NOT NULL LIMIT ${featureLimit}`,
  );
  const features: PreviewFeatureCollection['features'] = [];

  for (const row of result.toArray()) {
    const geoJson = row.toJSON()[GEOJSON_COLUMN];
    if (typeof geoJson !== 'string') continue;

    try {
      const geometry = JSON.parse(
        geoJson,
      ) as PreviewFeatureCollection['features'][number]['geometry'];
      if (geometry && typeof geometry.type === 'string') {
        features.push({ type: 'Feature', geometry, properties: {} });
      }
    } catch {
      // Skip malformed geometries without making the tabular preview unavailable.
    }
  }

  return { type: 'FeatureCollection', features };
}

async function readPreviewPage(
  iterator: AsyncIterator<PreviewBatch>,
  pendingRows: PreviewRow[],
): Promise<{ columns: string[]; rows: PreviewRow[]; done: boolean }> {
  const rows: PreviewRow[] = [];
  let columns: string[] = [];
  let done = false;

  while (rows.length < ROWS_PER_PAGE) {
    if (pendingRows.length === 0) {
      const next = await iterator.next();
      if (next.done) {
        done = true;
        break;
      }

      if (columns.length === 0) {
        columns = next.value.schema.fields.map(field => field.name);
      }
      pendingRows.push(...next.value.toArray().map(row => row.toJSON()));
      continue;
    }

    rows.push(...pendingRows.splice(0, ROWS_PER_PAGE - rows.length));
  }

  return { columns, rows, done };
}

function formatCell(value: unknown, isGeometry: boolean): string {
  if (value === null || value === undefined) return 'NULL';
  if (value instanceof Date) return value.toLocaleString();
  if (isGeometry) return String(value);
  if (typeof value === 'object') return JSON.stringify(value) ?? String(value);
  return String(value);
}

function ErrorMessage({ error }: { error: PreviewError }) {
  return (
    <div className="preview-error" role="alert">
      <p>{error.message}</p>
      {error.hint && <p>{error.hint}</p>}
    </div>
  );
}

export default function TabularPreview({
  resource,
  driver,
}: {
  resource: PreviewResource;
  driver: string;
}) {
  const previewRef = useRef<HTMLDivElement>(null);
  const tableContainerRef = useRef<HTMLDivElement>(null);
  const loadMoreRef = useRef<(() => Promise<void>) | null>(null);
  const hasManuallyResizedColumns = useRef(false);
  const visible = useVisible(previewRef);
  const layers = resource.metadata.layers ?? [];
  const [selectedLayerIndex, setSelectedLayerIndex] = useState(0);
  const activeLayerIndex = layers[selectedLayerIndex] ? selectedLayerIndex : 0;
  const activeLayer = layers[activeLayerIndex];
  const canRenderMap = Boolean(activeLayer?.geometryFields?.length);
  const [previewView, setPreviewView] = useState<'table' | 'map'>(() =>
    layers[0]?.geometryFields?.length ? 'map' : 'table',
  );
  const [mapFeatureLimit, setMapFeatureLimit] = useState(DEFAULT_MAP_FEATURE_LIMIT);
  const [mapFeatureLimitInput, setMapFeatureLimitInput] = useState(
    String(DEFAULT_MAP_FEATURE_LIMIT),
  );
  const requestedMapFeatureLimit = Number(mapFeatureLimitInput);
  const isValidMapFeatureLimit =
    Number.isSafeInteger(requestedMapFeatureLimit) && requestedMapFeatureLimit > 0;
  const hasChangedMapFeatureLimit =
    isValidMapFeatureLimit && requestedMapFeatureLimit !== mapFeatureLimit;
  const [result, setResult] = useState<QueryResult | null>(null);
  const [geoJsonData, setGeoJsonData] = useState<PreviewFeatureCollection | null>(null);
  const [mapError, setMapError] = useState<PreviewError | null>(null);
  const [error, setError] = useState<PreviewError | null>(null);
  const [loading, setLoading] = useState(false);
  const [loadingMore, setLoadingMore] = useState(false);
  const [columnSizing, setColumnSizing] = useState<ColumnSizingState>({});
  const columns: ColumnDef<PreviewRow, unknown>[] = (result?.columns ?? []).map(column => ({
    id: column,
    accessorFn: row => row[column],
    header: column,
    cell: info => formatCell(info.getValue(), result?.geometryColumns.includes(column) ?? false),
  }));
  const table = useReactTable({
    data: result?.rows ?? [],
    columns,
    getCoreRowModel: getCoreRowModel(),
    defaultColumn: { size: 240, minSize: 80, maxSize: 480 },
    columnResizeMode: 'onChange',
    onColumnSizingChange: updater => {
      hasManuallyResizedColumns.current = true;
      setColumnSizing(updater);
    },
    state: { columnSizing },
  });
  const rows = table.getRowModel().rows;
  const rowVirtualizer = useVirtualizer({
    count: rows.length,
    getScrollElement: () => tableContainerRef.current,
    estimateSize: () => 36,
    overscan: 10,
  });
  const virtualRows = rowVirtualizer.getVirtualItems();
  const paddingTop = virtualRows[0]?.start ?? 0;
  const lastVirtualRow = virtualRows[virtualRows.length - 1];
  const paddingBottom = lastVirtualRow ? rowVirtualizer.getTotalSize() - lastVirtualRow.end : 0;

  useEffect(() => {
    const container = tableContainerRef.current;
    const columnNames = result?.columns;
    if (!container || !columnNames?.length || hasManuallyResizedColumns.current) return;

    const fitColumns = () => {
      if (hasManuallyResizedColumns.current) return;
      const availableWidth = container.clientWidth;
      if (availableWidth <= 0) return;

      const size = Math.max(80, Math.min(480, availableWidth / columnNames.length));
      setColumnSizing(Object.fromEntries(columnNames.map(column => [column, size])));
    };

    fitColumns();
    if (typeof ResizeObserver === 'undefined') return;
    const observer = new ResizeObserver(fitColumns);
    observer.observe(container);
    return () => observer.disconnect();
  }, [result?.columns]);

  useEffect(() => {
    if (!visible || loading || !result?.hasMore || loadingMore) return;
    if ((lastVirtualRow?.index ?? -1) < result.rows.length - 20) return;

    void loadMoreRef.current?.();
  }, [lastVirtualRow?.index, loading, loadingMore, result, visible]);

  useEffect(() => {
    if (!visible) return;

    let cancelled = false;
    let iterator: AsyncIterator<PreviewBatch> | undefined;
    let geometryColumns: string[] = [];
    const pendingRows: PreviewRow[] = [];
    let isLoadingMore = false;
    let worker: Worker | undefined;
    let db: duckdb.AsyncDuckDB | undefined;
    let connection: duckdb.AsyncDuckDBConnection | undefined;

    setResult(null);
    setGeoJsonData(null);
    setMapError(null);
    setError(null);
    setLoading(true);
    setLoadingMore(false);
    setColumnSizing({});
    hasManuallyResizedColumns.current = false;
    loadMoreRef.current = async () => {
      if (cancelled || !iterator || isLoadingMore) return;

      isLoadingMore = true;
      setLoadingMore(true);
      try {
        const page = await readPreviewPage(iterator, pendingRows);
        if (cancelled) return;

        setResult(current => ({
          columns: current?.columns.length ? current.columns : page.columns,
          geometryColumns: current?.geometryColumns.length
            ? current.geometryColumns
            : geometryColumns,
          rows: [...(current?.rows ?? []), ...page.rows],
          hasMore: !page.done,
        }));
      } catch (caught) {
        if (!cancelled) {
          setError(toPreviewError(caught));
          setResult(current => (current ? { ...current, hasMore: false } : current));
        }
      } finally {
        isLoadingMore = false;
        if (!cancelled) setLoadingMore(false);
      }
    };

    async function run() {
      if (!resource.uri) {
        setError({ message: 'No resource URL found for this preview.' });
        setLoading(false);
        return;
      }

      setLoading(true);
      try {
        const bundle = await duckdb.selectBundle(bundles);
        if (cancelled) return;

        if (!bundle.mainWorker) {
          throw new Error('DuckDB worker bundle is unavailable.');
        }

        const workerUrl = URL.createObjectURL(
          new Blob([`importScripts(${JSON.stringify(bundle.mainWorker)});`], {
            type: 'text/javascript',
          }),
        );
        try {
          worker = new Worker(workerUrl);
          db = new duckdb.AsyncDuckDB(new duckdb.ConsoleLogger(), worker);
          await db.instantiate(bundle.mainModule, bundle.pthreadWorker);
        } finally {
          URL.revokeObjectURL(workerUrl);
        }
        if (cancelled) return;

        connection = await db.connect();
        const preview = await executePreview(connection, resource, driver, activeLayerIndex);
        geometryColumns = preview.geometryColumns;

        if (geometryColumns[0]) {
          const coordinateSystem = activeLayer?.geometryFields?.find(
            field => field.name === geometryColumns[0],
          )?.coordinateSystem?.projjson?.id;
          const sourceCrs =
            coordinateSystem?.authority && coordinateSystem.code !== undefined
              ? `${coordinateSystem.authority}:${coordinateSystem.code}`
              : undefined;

          try {
            const mapData = await readGeoJsonPreview(
              connection,
              preview.source,
              geometryColumns[0],
              sourceCrs,
              mapFeatureLimit,
            );
            if (!cancelled) setGeoJsonData(mapData);
          } catch (caught) {
            if (!cancelled) setMapError(toPreviewError(caught));
          }
        }

        const batches = await connection.send(preview.previewQuery);
        iterator = batches[Symbol.asyncIterator]();
        if (!cancelled) await loadMoreRef.current?.();
      } catch (caught) {
        if (!cancelled) {
          setError(toPreviewError(caught));
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    void run();

    return () => {
      cancelled = true;
      loadMoreRef.current = null;
      if (iterator?.return) void iterator.return();
      if (connection) void connection.close();
      if (db) void db.terminate();
      worker?.terminate();
    };
  }, [activeLayerIndex, driver, mapFeatureLimit, resource, visible]);

  return (
    <div
      ref={previewRef}
      className="preview"
      data-resource-id={resource.id}
      role="region"
      aria-label={`Preview of ${resource.title}`}
    >
      {layers.length > 1 && (
        <label className="preview-layer-select">
          <span>Layer</span>
          <select
            className="select"
            value={activeLayerIndex}
            onChange={event => {
              const nextIndex = Number(event.target.value);
              const nextLayer = layers[nextIndex];
              setSelectedLayerIndex(nextIndex);
              setPreviewView(nextLayer?.geometryFields?.length ? 'map' : 'table');
            }}
          >
            {layers.map((layer, index) => (
              <option key={`${layer.name}-${index}`} value={index}>
                {layer.name}
              </option>
            ))}
          </select>
        </label>
      )}
      {canRenderMap && (
        <div className="preview-map-controls">
          <div className="preview-view-toggle" role="group" aria-label="Preview view">
            <button
              className={`btn btn-sm ${previewView === 'map' ? 'btn-primary' : 'btn-ghost'}`}
              type="button"
              aria-pressed={previewView === 'map'}
              onClick={() => setPreviewView('map')}
            >
              Map
            </button>
            <button
              className={`btn btn-sm ${previewView === 'table' ? 'btn-primary' : 'btn-ghost'}`}
              type="button"
              aria-pressed={previewView === 'table'}
              onClick={() => setPreviewView('table')}
            >
              Table
            </button>
          </div>
          <div className="preview-map-limit">
            <label htmlFor="preview-map-feature-limit">Map feature limit</label>
            <input
              id="preview-map-feature-limit"
              className="input input-bordered input-sm"
              type="number"
              min="1"
              step="1"
              value={mapFeatureLimitInput}
              onChange={event => setMapFeatureLimitInput(event.target.value)}
              aria-describedby="preview-map-feature-limit-help"
              aria-invalid={!isValidMapFeatureLimit}
            />
            <button
              className="btn btn-sm btn-primary"
              type="button"
              disabled={!hasChangedMapFeatureLimit}
              onClick={() => setMapFeatureLimit(requestedMapFeatureLimit)}
            >
              Apply
            </button>
            <span id="preview-map-feature-limit-help" className="preview-map-limit-help">
              {isValidMapFeatureLimit
                ? 'Larger values may take longer to load.'
                : 'Enter a positive whole number.'}
            </span>
          </div>
        </div>
      )}
      {loading && <p role="status">Loading data preview…</p>}
      {error && <ErrorMessage error={error} />}
      {canRenderMap && previewView === 'map' && (
        <>
          {mapError && <ErrorMessage error={mapError} />}
          {!mapError && !geoJsonData && loading && <p role="status">Loading map preview…</p>}
          {geoJsonData && geoJsonData.features.length === 0 && <p>No geometries found.</p>}
          {geoJsonData && geoJsonData.features.length > 0 && (
            <>
              <Suspense fallback={<p role="status">Loading map renderer…</p>}>
                <GeoJsonPreview key={`${resource.id}-${activeLayerIndex}`} data={geoJsonData} />
              </Suspense>
              {geoJsonData.features.length === mapFeatureLimit && (
                <p>Map preview limited to the first {mapFeatureLimit.toLocaleString()} features.</p>
              )}
            </>
          )}
        </>
      )}
      {result && (previewView === 'table' || !canRenderMap) && (
        <>
          {result.columns.length > 0 && result.rows.length > 0 ? (
            <div ref={tableContainerRef} className="preview-table-wrap">
              <table
                className="table table-zebra table-sm"
                style={{
                  width: `${table.getTotalSize()}px`,
                  minWidth: '100%',
                  tableLayout: 'fixed',
                }}
              >
                <thead>
                  {table.getHeaderGroups().map(headerGroup => (
                    <tr key={headerGroup.id}>
                      {headerGroup.headers.map(header => (
                        <th
                          key={header.id}
                          scope="col"
                          style={{ width: `${header.getSize()}px` }}
                          title={header.column.id}
                        >
                          {!header.isPlaceholder && (
                            <>
                              {flexRender(header.column.columnDef.header, header.getContext())}
                              <button
                                type="button"
                                className="preview-column-resizer"
                                aria-label={`Resize ${header.column.id} column`}
                                onMouseDown={header.getResizeHandler()}
                                onTouchStart={header.getResizeHandler()}
                                onKeyDown={event => {
                                  if (event.key !== 'ArrowLeft' && event.key !== 'ArrowRight')
                                    return;
                                  event.preventDefault();
                                  const change = event.key === 'ArrowRight' ? 16 : -16;
                                  const nextSize = Math.max(
                                    header.column.columnDef.minSize ?? 80,
                                    Math.min(
                                      header.column.columnDef.maxSize ?? 480,
                                      header.getSize() + change,
                                    ),
                                  );
                                  table.setColumnSizing(current => ({
                                    ...current,
                                    [header.column.id]: nextSize,
                                  }));
                                }}
                              />
                            </>
                          )}
                        </th>
                      ))}
                    </tr>
                  ))}
                </thead>
                <tbody>
                  {paddingTop > 0 && (
                    <tr aria-hidden="true">
                      <td
                        colSpan={columns.length}
                        style={{ height: `${paddingTop}px`, padding: 0 }}
                      />
                    </tr>
                  )}
                  {virtualRows.map(virtualRow => {
                    const row = rows[virtualRow.index];
                    if (!row) return null;

                    return (
                      <tr key={row.id} style={{ height: `${virtualRow.size}px` }}>
                        {row.getVisibleCells().map(cell => (
                          <td
                            key={cell.id}
                            style={{ width: `${cell.column.getSize()}px` }}
                            title={formatCell(
                              cell.getValue(),
                              result.geometryColumns.includes(cell.column.id),
                            )}
                          >
                            {flexRender(cell.column.columnDef.cell, cell.getContext())}
                          </td>
                        ))}
                      </tr>
                    );
                  })}
                  {paddingBottom > 0 && (
                    <tr aria-hidden="true">
                      <td
                        colSpan={columns.length}
                        style={{ height: `${paddingBottom}px`, padding: 0 }}
                      />
                    </tr>
                  )}
                </tbody>
              </table>
              {loadingMore && <p role="status">Loading more rows…</p>}
            </div>
          ) : (
            <p>No rows returned.</p>
          )}
        </>
      )}
      {!visible && <p>Open this section to load the data preview.</p>}
    </div>
  );
}
