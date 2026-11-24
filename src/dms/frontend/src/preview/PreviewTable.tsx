import {
  flexRender,
  getCoreRowModel,
  useReactTable,
  type ColumnDef,
  type ColumnSizingState,
} from '@tanstack/react-table';
import { useVirtualizer } from '@tanstack/react-virtual';
import { useCallback, useEffect, useRef, useState } from 'react';

export const TABLE_PAGE_SIZE = 100;

export type PreviewRow = Record<string, unknown>;

export interface PreviewTablePage {
  columns: string[];
  geometryColumns: string[];
  rows: PreviewRow[];
  hasMore: boolean;
}

export type PreviewTableLoader = (offset: number, limit: number) => Promise<PreviewTablePage>;

function formatCell(value: unknown, isGeometry: boolean): string {
  if (value === null || value === undefined) return 'NULL';
  if (value instanceof Date) return value.toLocaleString();
  if (isGeometry) return String(value);
  if (value instanceof Uint8Array) return `[binary: ${value.byteLength} bytes]`;
  if (typeof value === 'object') {
    return (
      JSON.stringify(value, (_, item: unknown) =>
        typeof item === 'bigint' ? item.toString() : item,
      ) ?? String(value)
    );
  }
  return String(value);
}

export default function PreviewTable({
  resetKey,
  loadPage,
  onError,
}: {
  resetKey: string | number;
  loadPage: PreviewTableLoader;
  onError: (caught: unknown) => void;
}) {
  const tableContainerRef = useRef<HTMLDivElement>(null);
  const loadMoreRef = useRef<(() => Promise<void>) | null>(null);
  const isLoadingMoreRef = useRef(false);
  const resultRef = useRef<PreviewTablePage | null>(null);
  const loadPageRef = useRef(loadPage);
  const onErrorRef = useRef(onError);
  const hasManuallyResizedColumns = useRef(false);
  const [result, setResult] = useState<PreviewTablePage | null>(null);
  const [loadingMore, setLoadingMore] = useState(false);
  const [columnSizing, setColumnSizing] = useState<ColumnSizingState>({});

  loadPageRef.current = loadPage;
  onErrorRef.current = onError;

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

  const fitColumns = useCallback(() => {
    const container = tableContainerRef.current;
    const columnNames = result?.columns;
    if (!container || !columnNames?.length || hasManuallyResizedColumns.current) return;

    const availableWidth = container.clientWidth;
    if (availableWidth <= 0) return;

    const size = Math.max(80, Math.min(480, availableWidth / columnNames.length));
    setColumnSizing(Object.fromEntries(columnNames.map(column => [column, size])));
  }, [result?.columns]);

  useEffect(() => {
    fitColumns();
    const container = tableContainerRef.current;
    if (!container || typeof ResizeObserver === 'undefined') return;

    const observer = new ResizeObserver(fitColumns);
    observer.observe(container);
    return () => observer.disconnect();
  }, [fitColumns]);

  useEffect(() => {
    let cancelled = false;
    resultRef.current = null;
    isLoadingMoreRef.current = false;
    setResult(null);
    setLoadingMore(false);
    setColumnSizing({});
    hasManuallyResizedColumns.current = false;

    loadMoreRef.current = async () => {
      if (cancelled || isLoadingMoreRef.current || resultRef.current?.hasMore === false) return;

      isLoadingMoreRef.current = true;
      setLoadingMore(true);
      try {
        const current = resultRef.current;
        const page = await loadPageRef.current(current?.rows.length ?? 0, TABLE_PAGE_SIZE);
        if (cancelled) return;

        const next: PreviewTablePage = {
          columns: current?.columns.length ? current.columns : page.columns,
          geometryColumns: current?.geometryColumns.length
            ? current.geometryColumns
            : page.geometryColumns,
          rows: [...(current?.rows ?? []), ...page.rows],
          hasMore: page.hasMore,
        };
        resultRef.current = next;
        setResult(next);
      } catch (caught) {
        if (!cancelled) {
          onErrorRef.current(caught);
          const current = resultRef.current;
          if (current) {
            const next = { ...current, hasMore: false };
            resultRef.current = next;
            setResult(next);
          } else {
            const empty: PreviewTablePage = {
              columns: [],
              geometryColumns: [],
              rows: [],
              hasMore: false,
            };
            resultRef.current = empty;
            setResult(empty);
          }
        }
      } finally {
        if (!cancelled) {
          isLoadingMoreRef.current = false;
          setLoadingMore(false);
        }
      }
    };

    void loadMoreRef.current();
    return () => {
      cancelled = true;
      loadMoreRef.current = null;
    };
  }, [resetKey]);

  useEffect(() => {
    if (!result?.hasMore || loadingMore) return;
    if ((lastVirtualRow?.index ?? -1) < result.rows.length - 20) return;

    void loadMoreRef.current?.();
  }, [lastVirtualRow?.index, loadingMore, result]);

  if (!result && loadingMore) return <p role="status">Loading rows…</p>;
  if (result && result.columns.length === 0 && result.rows.length === 0) {
    return <p>No rows returned.</p>;
  }

  return result ? (
    result.rows.length > 0 ? (
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
                            if (event.key !== 'ArrowLeft' && event.key !== 'ArrowRight') return;
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
                <td colSpan={columns.length} style={{ height: `${paddingTop}px`, padding: 0 }} />
              </tr>
            )}
            {virtualRows.map(virtualRow => {
              const row = rows[virtualRow.index];
              if (!row) return null;

              return (
                <tr key={row.id} style={{ height: `${virtualRow.size}px` }}>
                  {row.getVisibleCells().map(cell => {
                    const value = formatCell(
                      cell.getValue(),
                      result.geometryColumns.includes(cell.column.id),
                    );
                    return (
                      <td
                        key={cell.id}
                        style={{ width: `${cell.column.getSize()}px` }}
                        title={value}
                      >
                        {flexRender(cell.column.columnDef.cell, cell.getContext())}
                      </td>
                    );
                  })}
                </tr>
              );
            })}
            {paddingBottom > 0 && (
              <tr aria-hidden="true">
                <td colSpan={columns.length} style={{ height: `${paddingBottom}px`, padding: 0 }} />
              </tr>
            )}
          </tbody>
        </table>
        {loadingMore && <p role="status">Loading more rows…</p>}
      </div>
    ) : (
      <p>No rows returned.</p>
    )
  ) : null;
}
