import TabularPreview from './TabularPreview';
import type { PreviewKind, PreviewResource } from './types';

interface AppProps {
  resource: PreviewResource;
  kind: PreviewKind;
  driver: string;
}

export default function App({ resource, kind, driver }: AppProps) {
  switch (kind) {
    case 'tabular':
      return <TabularPreview resource={resource} driver={driver} />;
    case 'raster':
      return <p>Raster preview is not available yet.</p>;
    default:
      return <p>Preview is not available for this resource type.</p>;
  }
}
