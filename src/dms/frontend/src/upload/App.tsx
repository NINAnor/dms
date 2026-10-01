import { UppyContextProvider } from '@uppy/react';
import { useEffect, useState } from 'react';
import { Uppy, type UppyFile } from '@uppy/core';
import AwsS3 from '@uppy/aws-s3';
import { Dashboard } from './Dashboard';

import '@uppy/core/css/style.min.css';
import '@uppy/dashboard/css/style.min.css';

import { client, config } from './config';
import type { Storage } from './types';

interface Meta {
  key?: string;
  [key: string]: unknown;
}

// Files larger than this threshold use S3 multipart upload instead of a single PUT.
const MULTIPART_THRESHOLD = 100 * 1024 * 1024; // 100 MB

function uploadUrl(path: string) {
  return `/api/v1/datasets/${config.dataset}/${path}`;
}

export default function App() {
  const [storage, setStorage] = useState<Storage | null>(null);
  const [uppy] = useState(() => new Uppy<Meta>());

  useEffect(() => {
    client.get<Storage[]>(uploadUrl('available-storages/')).then(({ data }) => {
      setStorage(data[0] ?? null);
    });
  }, []);

  useEffect(() => {
    if (!storage) return;

    uppy.use(AwsS3, {
      shouldUseMultipart: file => (file.size ?? 0) > MULTIPART_THRESHOLD,
      getUploadParameters: async file => {
        const { data } = await client.post(uploadUrl('upload-url/'), {
          storage: storage.id,
          filename: file.name,
        });
        uppy.setFileMeta(file.id, { key: data.key });
        return { method: 'PUT', url: data.upload_url };
      },
      createMultipartUpload: async file => {
        const { data } = await client.post(uploadUrl('upload-url/'), {
          storage: storage.id,
          filename: file.name,
          multipart: true,
        });
        uppy.setFileMeta(file.id, { key: data.key });
        return { uploadId: data.upload_id, key: data.key };
      },
      listParts: async () => [],
      signPart: async (_file, { uploadId, key, partNumber }) => {
        const { data } = await client.post(uploadUrl('upload-url/sign-part/'), {
          storage: storage.id,
          key,
          upload_id: uploadId,
          part_number: partNumber,
        });
        return { method: 'PUT', url: data.url };
      },
      abortMultipartUpload: async (_file, { key, uploadId }) => {
        await client.post(uploadUrl('upload-url/abort-multipart/'), {
          storage: storage.id,
          key,
          upload_id: uploadId,
        });
      },
      completeMultipartUpload: async (_file, { key, uploadId, parts }) => {
        await client.post(uploadUrl('upload-url/complete-multipart/'), {
          storage: storage.id,
          key,
          upload_id: uploadId,
          parts,
        });
        return {};
      },
    });

    return () => {
      const plugin = uppy.getPlugin('AwsS3');
      if (plugin) uppy.removePlugin(plugin);
    };
  }, [uppy, storage]);

  useEffect(() => {
    const handler = (file?: UppyFile<Meta, Record<string, never>>) => {
      const key = file?.meta?.key;
      if (!key || !storage) return;
      client.post(uploadUrl('resources/confirm-upload/'), {
        storage: storage.id,
        key,
      });
    };
    uppy.on('upload-success', handler);
    return () => {
      uppy.off('upload-success', handler);
    };
  }, [uppy, storage]);

  if (!storage) {
    return <p>Loading storages…</p>;
  }

  return (
    <UppyContextProvider uppy={uppy}>
      <Dashboard />
    </UppyContextProvider>
  );
}
