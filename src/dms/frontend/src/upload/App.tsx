import { UppyContextProvider } from '@uppy/react';
import { useEffect, useState } from 'react';
import { Uppy } from '@uppy/core';
import AwsS3 from '@uppy/aws-s3';
import toast, { Toaster } from 'react-hot-toast';
import { Dashboard } from './Dashboard';

import '@uppy/core/css/style.min.css';
import '@uppy/dashboard/css/style.min.css';

import { client, config } from './config';
import type { Storage } from './types';

interface Meta {
  [key: string]: unknown;
}

// Files larger than this threshold use S3 multipart upload instead of a single PUT.
const MULTIPART_THRESHOLD = 100 * 1024 * 1024; // 100 MB

function uploadUrl(path: string) {
  return `/api/v1/datasets/${config.dataset}/${path}`;
}

export default function App() {
  const [storages, setStorages] = useState<Storage[] | null>(null);
  const [storageId, setStorageId] = useState<number | null>(null);
  const [uppy] = useState(() => new Uppy<Meta>());

  useEffect(() => {
    client.get<Storage[]>(uploadUrl('available-storages/')).then(({ data }) => {
      setStorages(data);
      // Auto-select when there is exactly one option; otherwise let the
      // user pick explicitly (or leave unset when there are none).
      if (data.length === 1) {
        setStorageId(data[0].id);
      }
    });
  }, []);

  useEffect(() => {
    if (!storageId) return;

    uppy.use(AwsS3, {
      shouldUseMultipart: file => (file.size ?? 0) > MULTIPART_THRESHOLD,
      // Preserve the filename as the S3 key (no randomization), matching the
      // backend's previous behavior.
      generateObjectKey: file => file.name ?? file.id,
      // The backend presigns each raw S3 request behind a single endpoint,
      // so we can forward Uppy's request almost verbatim.
      signRequest: async request => {
        const { data } = await client.post(uploadUrl('sign-s3-request/'), {
          storage: storageId,
          ...request,
        });
        return data;
      },
    });

    return () => {
      const plugin = uppy.getPlugin('AwsS3');
      if (plugin) uppy.removePlugin(plugin);
    };
  }, [uppy, storageId]);

  useEffect(() => {
    const handler = (file?: { id: string; name?: string | null }) => {
      // Use the original filename (matching `generateObjectKey` above), not
      // the resolved S3 path from the upload-success event -- the backend
      // re-applies the storage's prefix template to whatever key we send
      // here, so sending the already-prefixed path would double it.
      const key = file?.name ?? file?.id;
      if (!key || !storageId) return;
      client
        .post(uploadUrl('resources/confirm-upload/'), {
          storage: storageId,
          key,
        })
        .then(() => {
          toast.success(`"${key}" uploaded and queued for processing.`);
        });
    };
    uppy.on('upload-success', handler);
    return () => {
      uppy.off('upload-success', handler);
    };
  }, [uppy, storageId]);

  if (storages === null) {
    return <p>Loading storages…</p>;
  }

  if (storages.length === 0) {
    return (
      <p className="text-error">
        No storage is configured for this dataset's project. Uploads are disabled until a storage is
        made available.
      </p>
    );
  }

  return (
    <UppyContextProvider uppy={uppy}>
      <Toaster position="top-right" />
      <div>
        {storages.length > 1 && (
          <div className="mb-3">
            <label htmlFor="storage-select" className="mb-1 block font-bold">
              Storage
            </label>
            <select
              id="storage-select"
              className="select select-bordered"
              value={storageId ?? ''}
              onChange={e => setStorageId(Number(e.target.value))}
            >
              <option value="" disabled>
                Select a storage…
              </option>
              {storages.map(s => (
                <option key={s.id} value={s.id}>
                  {s.name}
                </option>
              ))}
            </select>
          </div>
        )}
        {storageId && <Dashboard />}
      </div>
    </UppyContextProvider>
  );
}
