import { Handle, Position, NodeProps, NodeToolbar } from '@xyflow/react';
import { LabeledHandle } from './Handle';
import { AppNode, Option } from '../types';
import cn from 'classnames';
import { config } from '../config';
import useStore from '../store';
import { useCallback, useState } from 'react';

export function DatasetNode({ data, selected, id, ...props }: NodeProps<AppNode>) {
  const addRelTypeToNode = useStore(state => state.addRelTypeToNode);
  const [selectedRel, setSelectedRel] = useState('');

  const addRelType = useCallback(() => {
    addRelTypeToNode(id, selectedRel);
    setSelectedRel('');
  }, [id, selectedRel]);

  return (
    <div
      className={cn('shadow-md rounded-md  border-2  max-w-sm', {
        'bg-white border-stone-400': !selected,
        'bg-yellow-200 border-yellow-500': selected,
      })}
    >
      <NodeToolbar isVisible={selected} position={Position.Top} align="center">
        <div className="flex">
          <select
            className="border-primary text-primary rounded-s-lg"
            value={selectedRel}
            onChange={e => setSelectedRel(e.target.value)}
          >
            {config.relTypes.map((rt: Option) => (
              <option key={rt.value} value={rt.value}>
                {rt.label}
              </option>
            ))}
          </select>
          <button
            className="btn btn-outline text-primary rounded-s-none border-s-0"
            disabled={!selectedRel}
            onClick={addRelType}
          >
            <i className="fas fa-plus"></i> Relation Type
          </button>
        </div>
      </NodeToolbar>
      <div className="p-5">
        <a href={data.url} target="_blank" className="nodrag nopan mr-1">
          <i className="fas fa-link"></i>
        </a>
        {data?.label}
      </div>
      <Handle type="target" position={Position.Left} className="h-10 rounded-full !bg-green-500" style={{ top: 30 }} />
      {data.relationshipTypes.map(r => (
        <LabeledHandle
          key={r}
          position={Position.Right}
          title={r}
          type="source"
          id={r}
          className="last-child:rounded-b"
        />
      ))}
    </div>
  );
}
