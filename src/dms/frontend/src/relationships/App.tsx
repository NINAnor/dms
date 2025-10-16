import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'react-hot-toast';
import { ReactFlow, Background, Controls, MarkerType } from '@xyflow/react';
import { useShallow } from 'zustand/react/shallow';

const queryClient = new QueryClient();

import useStore from './store';
import { AppState } from './types';
import { edgeTypes, nodeTypes } from './components/graphTypes';
import { useEffect } from 'react';
import { ManageNode } from './components/ManageNode';

const selector = (state: AppState) => ({
  nodes: state.nodes,
  edges: state.edges,
  onNodesChange: state.onNodesChange,
  onEdgesChange: state.onEdgesChange,
  onConnect: state.onConnect,
  applyLayout: state.applyLayout,
});

const defaultEdgeOptions = {
  type: 'smart',
  style: {
    strokeWidth: 2,
  },
  markerEnd: {
    type: MarkerType.ArrowClosed,
    color: '#b1b1b7',
  },
};

const snapGrid = [20, 20] as [number, number];

function App() {
  const { nodes, edges, onNodesChange, onEdgesChange, onConnect, applyLayout } = useStore(useShallow(selector));

  useEffect(() => {
    setTimeout(applyLayout, 100);
  }, []);

  return (
    <QueryClientProvider client={queryClient}>
      <Toaster />
      <div style={{ width: '100%', height: 'calc(100vh - 64px - 10rem)' }}>
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          fitView
          nodeTypes={nodeTypes}
          edgeTypes={edgeTypes}
          defaultEdgeOptions={defaultEdgeOptions}
          snapGrid={snapGrid}
          snapToGrid
        >
          <Background />
          <Controls />
          <ManageNode />
        </ReactFlow>
      </div>
    </QueryClientProvider>
  );
}

export default App;
