import { create } from 'zustand';
import { addEdge, applyNodeChanges, applyEdgeChanges } from '@xyflow/react';

import { type AppState } from './types';
import { config } from './config';
import { graphLayout } from './utils';

const initialNodes = graphLayout(config.nodes, config.edges);

// this is our useStore hook that we can use in our components to get parts of the store and call actions
const useStore = create<AppState>((set, get) => ({
  nodes: initialNodes ?? [],
  edges: config.edges ?? [],
  onNodesChange: changes => {
    set({
      nodes: applyNodeChanges(changes, get().nodes),
    });
  },
  onEdgesChange: changes => {
    set({
      edges: applyEdgeChanges(changes, get().edges),
    });
  },
  onConnect: connection => {
    set({
      edges: addEdge({ ...connection, id: crypto.randomUUID() }, get().edges),
    });
  },
  setNodes: nodes => {
    set({ nodes });
  },
  setEdges: edges => {
    set({ edges });
  },
  applyLayout: () => {
    const { nodes, edges } = get();
    set({
      nodes: graphLayout(nodes, edges),
    });
  },
  addRelTypeToNode: (id: string, relationshipType: string) => {
    const { nodes } = get();
    set({
      nodes: nodes.map(e => {
        if (e.id === id) {
          e.data.relationshipTypes = [...e.data.relationshipTypes, relationshipType];
        }
        return e;
      }),
    });
  },
}));

export default useStore;
