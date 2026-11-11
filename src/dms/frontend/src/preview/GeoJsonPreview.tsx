import { GeoJsonLayer } from '@deck.gl/layers';
import DeckGL from '@deck.gl/react';
import Map from 'react-map-gl/maplibre';

import 'maplibre-gl/dist/maplibre-gl.css';

import type { PreviewFeatureCollection } from './types';

function getInitialViewState(data: PreviewFeatureCollection) {
  const coordinates: Array<[number, number]> = [];

  function collect(value: unknown) {
    if (!Array.isArray(value)) return;
    if (typeof value[0] === 'number' && typeof value[1] === 'number') {
      coordinates.push([value[0], value[1]]);
      return;
    }
    value.forEach(collect);
  }

  data.features.forEach(feature => {
    if (feature.geometry && 'coordinates' in feature.geometry) {
      collect(feature.geometry.coordinates);
    }
  });
  if (coordinates.length === 0) {
    return { longitude: 0, latitude: 0, zoom: 1 };
  }

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

export default function GeoJsonPreview({ data }: { data: PreviewFeatureCollection }) {
  const layer = new GeoJsonLayer({
    id: 'geoparquet-features',
    data,
    filled: true,
    stroked: true,
    pointType: 'circle',
    getFillColor: [30, 110, 93, 110],
    getLineColor: [20, 84, 72, 220],
    getPointRadius: 4,
    pointRadiusUnits: 'pixels',
    lineWidthMinPixels: 1,
  });

  return (
    <div className="geo-preview-map" aria-label="GeoParquet map preview">
      <DeckGL
        initialViewState={getInitialViewState(data)}
        controller
        layers={[layer]}
        style={{ position: 'relative', width: '100%', height: '100%' }}
      >
        <Map mapStyle="https://tiles.openfreemap.org/styles/bright" />
      </DeckGL>
    </div>
  );
}
