import { UppyContext } from '@uppy/react';
import UppyDashboard from '@uppy/react/dashboard';

import { useContext } from 'react';

export function Dashboard() {
  const { uppy } = useContext(UppyContext);

  return (
    <div>
      <div className="flex justify-between mb-3">
        <h1 className="font-bold text-3xl">Upload resources</h1>
        <a href="../../" className="btn btn-primary">
          Back
        </a>
      </div>
      <p className="mb-5">
        Uploaded files will be processed in background, it could take some time before they are shown in the dataset
      </p>
      <UppyDashboard id="dashboard" uppy={uppy!} />
    </div>
  );
}
