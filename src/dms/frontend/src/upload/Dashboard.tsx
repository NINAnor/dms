import { UppyContext } from '@uppy/react';
import UppyDashboard from '@uppy/react/dashboard';

import { useContext } from 'react';

export function Dashboard() {
  const { uppy } = useContext(UppyContext);

  return (
    <div>
      <h1 className="font-bold text-3xl mb-5">Upload resources</h1>
      <UppyDashboard id="dashboard" uppy={uppy!} />
    </div>
  );
}
