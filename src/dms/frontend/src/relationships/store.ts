import { create } from 'zustand';
import { addEdge, applyNodeChanges, applyEdgeChanges, Edge } from '@xyflow/react';

import { Dataset, Relationship, type AppState } from './types';
import { client, config } from './config';
import { graphLayout, relToEdge } from './utils';
import toast from 'react-hot-toast';

const initialNodes = graphLayout(config.nodes, config.edges);

// this is our useStore hook that we can use in our components to get parts of the store and call actions
const useStore = create<AppState>((set, get) => ({
  nodes: initialNodes ?? [],
  edges: config.edges ?? [],
  edgeIndex: new Set(config.edges.map((e: Edge) => e.id)),
  onNodesChange: changes => {
    set({
      nodes: applyNodeChanges(changes, get().nodes),
    });
  },
  onEdgesChange: changes => {
    const promises = changes.map(async c => {
      if (c.type == 'remove') {
        try {
          await client.delete(`${config.urls.datasetRelationshipList}${c.id}/`);
          return c;
        } catch (e) {
          console.error(e);
          toast.error('Failed');
          return null;
        }
      }

      return c;
    });
    Promise.all(promises).then(ch => {
      return set({
        edges: applyEdgeChanges(
          ch.filter(o => o !== null),
          get().edges,
        ),
      });
    });
  },
  onConnect: connection => {
    client
      .post(config.urls.datasetRelationshipList, {
        source: connection.source,
        target: connection.target,
        type: connection.sourceHandle,
      })
      .then(response => {
        set({
          edges: addEdge({ ...connection, id: response.data.uuid }, get().edges),
        });
      })
      .catch(e => {
        console.error(e);
        toast.error('failed');
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
  addDataset: (dataset: Dataset, relationships: Relationship[]) => {
    const { nodes, edges, edgeIndex } = get();

    const newEdges = [...edges, ...relationships.filter(r => !edgeIndex.has(r.uuid)).map(r => relToEdge(r))];

    set({
      edgeIndex: new Set(newEdges.map(e => e.id)),
      nodes: graphLayout(
        [
          ...nodes,
          {
            id: dataset.id,
            type: 'dataset',
            data: {
              url: dataset.url,
              relationshipTypes: Array.from(
                new Set(relationships.filter(r => r.source_id == dataset.id).map(r => r.type)),
              ),
              label: dataset.title,
            },
            position: {
              x: 0,
              y: 0,
            },
          },
        ],
        newEdges,
      ),
      edges: newEdges,
    });
    toast.success('Successfully loaded ' + dataset.title);
  },
}));

export default useStore;
