import { type Edge, type Node, type OnNodesChange, type OnEdgesChange, type OnConnect } from '@xyflow/react';

export type AppNode = Node<{
  label: string;
  relationshipTypes: string[];
  url: string;
}>;

export type Dataset = {
  id: string;
  url: string;
  title: string;
};

export type Relationship = {
  uuid: string;
  source_id: string;
  target_id: string;
  type: string;
};

export type AppState = {
  nodes: AppNode[];
  edges: Edge[];
  edgeIndex: Set<string>;
  onNodesChange: OnNodesChange<AppNode>;
  onEdgesChange: OnEdgesChange;
  onConnect: OnConnect;
  setNodes: (nodes: AppNode[]) => void;
  setEdges: (edges: Edge[]) => void;
  applyLayout: () => void;
  addRelTypeToNode: (id: string, relationshipType: string) => void;
  addDataset: (dataset: Dataset, relationships: Relationship[]) => void;
};

export type Option = {
  label: string;
  value: string;
};
