import maplibregl from 'maplibre-gl';
import { useEffect, useMemo, useRef, useState } from 'react';

import 'maplibre-gl/dist/maplibre-gl.css';

import type { GdalRasterBand, PreviewResource } from './types';

type RenderMode = 'single' | 'rgb';

const colormaps = [
  'viridis',
  'plasma',
  'inferno',
  'magma',
  'cividis',
  'gray',
  'turbo',
  'terrain',
  'spectral',
  'rdylbu',
  'coolwarm',
  'rainbow',
];

interface RenderConfiguration {
  mode: RenderMode;
  singleBand: number;
  colormapName: string;
  redBand: number;
  greenBand: number;
  blueBand: number;
  minimum: string;
  maximum: string;
}

function findBand(bands: GdalRasterBand[], interpretation: string) {
  return bands.find(
    band => band.colorInterpretation?.toLowerCase() === interpretation.toLowerCase(),
  );
}

function getBandRange(band: GdalRasterBand | undefined) {
  const minimum = band?.minimum !== undefined && Number.isFinite(band.minimum) ? band.minimum : 0;
  const maximum = band?.maximum !== undefined && Number.isFinite(band.maximum) ? band.maximum : 1;

  return {
    minimum: String(minimum),
    maximum: String(maximum),
  };
}

function guessConfiguration(bands: GdalRasterBand[]): RenderConfiguration {
  const red = findBand(bands, 'Red');
  const green = findBand(bands, 'Green');
  const blue = findBand(bands, 'Blue');
  const colorBands = bands.filter(band => band.colorInterpretation?.toLowerCase() !== 'alpha');
  const gray = findBand(bands, 'Gray') ?? colorBands[0] ?? bands[0];
  const rgbBands = red && green && blue ? [red, green, blue] : colorBands.slice(0, 3);
  const range = getBandRange(gray);

  return {
    mode: red && green && blue ? 'rgb' : 'single',
    singleBand: gray?.band ?? 1,
    colormapName: 'viridis',
    redBand: rgbBands[0]?.band ?? 1,
    greenBand: rgbBands[1]?.band ?? 1,
    blueBand: rgbBands[2]?.band ?? 1,
    ...range,
  };
}

function createTileJsonUrl(tileJsonUrl: string, configuration: RenderConfiguration): string {
  const url = new URL(tileJsonUrl, window.location.href);
  url.searchParams.delete('bidx');
  url.searchParams.delete('rescale');
  url.searchParams.delete('colormap_name');

  if (configuration.mode === 'single') {
    url.searchParams.append('bidx', String(configuration.singleBand));
    url.searchParams.set('colormap_name', configuration.colormapName);

    const minimum = Number(configuration.minimum);
    const maximum = Number(configuration.maximum);
    if (
      configuration.minimum.trim() &&
      configuration.maximum.trim() &&
      Number.isFinite(minimum) &&
      Number.isFinite(maximum) &&
      minimum < maximum
    ) {
      url.searchParams.set('rescale', `${minimum},${maximum}`);
    }
  } else {
    url.searchParams.append('bidx', String(configuration.redBand));
    url.searchParams.append('bidx', String(configuration.greenBand));
    url.searchParams.append('bidx', String(configuration.blueBand));
  }

  return url.toString();
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

export default function RasterPreview({ resource }: { resource: PreviewResource }) {
  const configurationKey = `${resource.id}:${resource.uri}:${JSON.stringify(resource.metadata.bands ?? [])}`;

  return <RasterPreviewContent key={configurationKey} resource={resource} />;
}

function RasterPreviewContent({ resource }: { resource: PreviewResource }) {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<maplibregl.Map | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const bands = resource.metadata.bands ?? [];
  const colorBands = bands.filter(band => band.colorInterpretation?.toLowerCase() !== 'alpha');
  const canRenderRgb = colorBands.length >= 3;
  const [configuration, setConfiguration] = useState(() => guessConfiguration(bands));
  const [appliedConfiguration, setAppliedConfiguration] = useState(configuration);
  const hasValidRange =
    configuration.mode !== 'single' ||
    (configuration.minimum.trim() !== '' &&
      configuration.maximum.trim() !== '' &&
      Number(configuration.minimum) < Number(configuration.maximum) &&
      Number.isFinite(Number(configuration.minimum)) &&
      Number.isFinite(Number(configuration.maximum)));
  const configurationChanged = Object.keys(configuration).some(
    key =>
      configuration[key as keyof RenderConfiguration] !==
      appliedConfiguration[key as keyof RenderConfiguration],
  );
  const tileJsonUrl = useMemo(
    () => createTileJsonUrl(resource.uri, appliedConfiguration),
    [appliedConfiguration, resource.uri],
  );
  const tileJsonUrlRef = useRef(tileJsonUrl);
  tileJsonUrlRef.current = tileJsonUrl;

  function updateConfiguration(patch: Partial<RenderConfiguration>) {
    setConfiguration(current => ({ ...current, ...patch }));
  }

  function selectSingleBand(bandNumber: number) {
    const selectedBand = bands.find(band => band.band === bandNumber);
    updateConfiguration({ singleBand: bandNumber, ...getBandRange(selectedBand) });
  }

  function renderBandSelect(label: string, value: number, onChange: (band: number) => void) {
    return (
      <label className="raster-preview-control">
        <span>{label}</span>
        <select
          className="select select-bordered"
          value={value}
          onChange={event => onChange(Number(event.target.value))}
        >
          {colorBands.map(band => (
            <option key={band.band} value={band.band}>
              Band {band.band}
              {band.colorInterpretation ? ` · ${band.colorInterpretation}` : ''}
            </option>
          ))}
        </select>
      </label>
    );
  }

  useEffect(() => {
    const container = mapContainerRef.current;
    if (!container) return;

    const bounds = getWgs84Bounds(resource.metadata.wgs84Extent);
    let map: maplibregl.Map;
    setLoading(true);
    setError(null);

    try {
      map = new maplibregl.Map({
        container,
        style: 'https://tiles.openfreemap.org/styles/bright',
        center: [10, 72],
        zoom: 2,
      });
      map.addControl(new maplibregl.NavigationControl(), 'top-right');
      map.addControl(new maplibregl.ScaleControl({ maxWidth: 80, unit: 'metric' }));

      map.once('load', () => {
        try {
          map.addSource('raster-preview', {
            type: 'raster',
            url: tileJsonUrlRef.current,
            tileSize: 256,
          });
          map.addLayer({ id: 'raster-preview-layer', type: 'raster', source: 'raster-preview' });
          if (bounds) map.fitBounds(bounds, { padding: 24 });
          setLoading(false);
        } catch (caught) {
          setError(caught instanceof Error ? caught.message : String(caught));
          setLoading(false);
        }
      });

      map.on('error', event => {
        if (event.error) {
          setError(event.error.message);
          setLoading(false);
        }
      });

      const observer = new ResizeObserver(() => map.resize());
      observer.observe(container);
      mapRef.current = map;
      return () => {
        observer.disconnect();
        mapRef.current = null;
        map.remove();
      };
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : String(caught));
      setLoading(false);
    }
  }, [resource.id, resource.metadata.wgs84Extent, resource.uri]);

  useEffect(() => {
    const source = mapRef.current?.getSource('raster-preview');
    if (source instanceof maplibregl.RasterTileSource) {
      source.setUrl(tileJsonUrl);
    }
  }, [tileJsonUrl]);

  return (
    <div className="raster-preview" aria-label={`Raster preview of ${resource.title}`}>
      <div className="raster-preview-controls">
        <label className="raster-preview-control">
          <span>Render as</span>
          <select
            className="select select-bordered"
            value={configuration.mode}
            onChange={event => updateConfiguration({ mode: event.target.value as RenderMode })}
          >
            <option value="single">Single band</option>
            {canRenderRgb && <option value="rgb">RGB</option>}
          </select>
        </label>

        {configuration.mode === 'single' ? (
          <>
            {renderBandSelect('Band', configuration.singleBand, selectSingleBand)}
            <label className="raster-preview-control">
              <span>Colormap</span>
              <select
                className="select select-bordered"
                value={configuration.colormapName}
                onChange={event => updateConfiguration({ colormapName: event.target.value })}
              >
                {colormaps.map(colormap => (
                  <option key={colormap} value={colormap}>
                    {colormap}
                  </option>
                ))}
              </select>
            </label>
            <label className="raster-preview-control">
              <span>Minimum</span>
              <input
                className="input input-bordered"
                type="number"
                step="any"
                value={configuration.minimum}
                onChange={event => updateConfiguration({ minimum: event.target.value })}
              />
            </label>
            <label className="raster-preview-control">
              <span>Maximum</span>
              <input
                className="input input-bordered"
                type="number"
                step="any"
                value={configuration.maximum}
                onChange={event => updateConfiguration({ maximum: event.target.value })}
              />
            </label>
            {!hasValidRange && (
              <p className="preview-error" role="alert">
                Minimum must be less than maximum.
              </p>
            )}
          </>
        ) : (
          <>
            {renderBandSelect('Red band', configuration.redBand, band =>
              updateConfiguration({ redBand: band }),
            )}
            {renderBandSelect('Green band', configuration.greenBand, band =>
              updateConfiguration({ greenBand: band }),
            )}
            {renderBandSelect('Blue band', configuration.blueBand, band =>
              updateConfiguration({ blueBand: band }),
            )}
          </>
        )}
        <button
          className="btn btn-primary"
          type="button"
          disabled={!configurationChanged || !hasValidRange}
          onClick={() => setAppliedConfiguration(configuration)}
        >
          Apply
        </button>
      </div>
      {loading && <p role="status">Loading raster preview…</p>}
      {error && (
        <div className="preview-error" role="alert">
          <p>{error}</p>
          <p>Check that TiTiler, the raster source, and the basemap are reachable.</p>
        </div>
      )}
      <div ref={mapContainerRef} className="raster-preview-map" />
    </div>
  );
}
