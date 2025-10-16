import { type Edge, type Node, type OnNodesChange, type OnEdgesChange, type OnConnect } from '@xyflow/react';

export type AppNode = Node<{
  label: string;
  relationshipTypes: string[];
  url: string;
}>;

export type AppState = {
  nodes: AppNode[];
  edges: Edge[];
  onNodesChange: OnNodesChange<AppNode>;
  onEdgesChange: OnEdgesChange;
  onConnect: OnConnect;
  setNodes: (nodes: AppNode[]) => void;
  setEdges: (edges: Edge[]) => void;
  applyLayout: () => void;
  addRelTypeToNode: (id: string, relationshipType: string) => void;
};

export type Option = {
  label: string;
  value: string;
};
