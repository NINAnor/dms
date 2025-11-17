import { UppyContextProvider } from '@uppy/react';
import { useEffect, useState } from 'react';
import { Uppy, UppyFile } from '@uppy/core';
import { Dashboard } from './Dashboard';

import '@uppy/core/css/style.min.css';
import '@uppy/dashboard/css/style.min.css';

import AwsS3, { type AwsS3UploadParameters, type AwsS3MultipartOptions } from '@uppy/aws-s3';
import { config, client } from './config';
import { AxiosResponse } from 'axios';

type Meta = Record<string, unknown>;
type Body = Record<string, unknown>;

const AWS_OPTIONS: AwsS3MultipartOptions<Meta, Body> = {
  async getUploadParameters(
    file: UppyFile<Meta, Body>,
    { signal: _signal }: { signal?: AbortSignal } = {},
  ): Promise<AwsS3UploadParameters> {
    const response = await client.post<any, AxiosResponse<AwsS3UploadParameters>>(config.endpoint, {
      filename: file.name,
    });
    return await response.data;
  },
  endpoint: '',
};
export default function App() {
  const [uppy] = useState(() => new Uppy<Meta>().use(AwsS3, AWS_OPTIONS));

  useEffect(() => {
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
