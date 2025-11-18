import { UppyContextProvider } from '@uppy/react';
import { useEffect, useState } from 'react';
import { Uppy } from '@uppy/core';
import { Dashboard } from './Dashboard';
import Tus from '@uppy/tus';

import '@uppy/core/css/style.min.css';
import '@uppy/dashboard/css/style.min.css';

import { config } from './config';

type Meta = Record<string, unknown>;

export default function App() {
  const [uppy] = useState(() =>
    new Uppy<Meta>().use(Tus, {
      endpoint: config.endpoint,
      async onBeforeRequest(req) {
        req.setHeader('Authorization', `Bearer ${config.token}`);
      },
    }),
  );

  useEffect(() => {
    uppy.on('file-added', file => {
      uppy.setFileMeta(file.id, {
        dataset: config.dataset,
      });
    });
    uppy.on('upload-success', (file, response) => {
      console.debug('Uploaded', file, response);
    });
  }, [uppy]);

  return (
    <UppyContextProvider uppy={uppy}>
      <Dashboard />
    </UppyContextProvider>
  );
}
