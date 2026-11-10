import React from 'react';
import ReactDOM from 'react-dom/client';

import App from './App';
import type { GdalMetadata, PreviewKind, PreviewResource } from './types';
import './index.css';

const rootElement = document.getElementById('resource-preview');
const metadataElement = document.getElementById('resource-preview-metadata');

if (rootElement) {
  const resource: PreviewResource = {
    id: rootElement.dataset.resourceId ?? '',
    title: rootElement.dataset.resourceTitle ?? '',
    uri: rootElement.dataset.resourceUri ?? '',
    metadata: JSON.parse(metadataElement?.textContent ?? '{}') as GdalMetadata,
  };
  const kind = (rootElement.dataset.previewKind ?? '') as PreviewKind;
  const driver = rootElement.dataset.previewType ?? '';

  ReactDOM.createRoot(rootElement).render(
    <React.StrictMode>
      <App resource={resource} kind={kind} driver={driver} />
    </React.StrictMode>,
  );
}
