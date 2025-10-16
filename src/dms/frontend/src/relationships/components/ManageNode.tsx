import { useQuery } from '@tanstack/react-query';
import { Panel } from '@xyflow/react';
import { useMemo, useState } from 'react';
import { client, config } from '../config';
import useStore from '../store';
import { Dataset } from '../types';
import classNames from 'classnames';

export function ManageNode() {
  const [search, setSearch] = useState('');
  const [collapsed, setCollapsed] = useState(true);
  const query = useMemo(
    () => ({
      queryKey: ['dataset', search],
      queryFn: async () => {
        if (!search) {
          return {
            results: [],
          };
        }
        const res = await client.get(config.urls.datasetList, {
          params: {
            search,
          },
        });
        return res.data;
      },
    }),
    [search],
  );
  const { isPending, error, data, isSuccess } = useQuery(query);
  const addDataset = useStore(state => state.addDataset);

  return (
    <Panel position="top-right" className="bg-white p-2 border-2 rounded w-[24rem]">
      <div className="flex justify-between">
        <h3 className="text-lg font-bold">Load Datasets</h3>
        <button onClick={() => setCollapsed(!collapsed)}>
          <i className={classNames('fas', { 'fa-caret-down': collapsed, 'fa-caret-up': !collapsed })}></i>
        </button>
      </div>
      {!collapsed && (
        <>
          <div className="flex flex-col mt-2">
            <label>Search</label>
            <input className="rounded" value={search} onChange={e => setSearch(e.target.value)} />
          </div>
          <div className="flex flex-col gap-2 mt-2 text-sm">
            {isPending && (
              <div>
                <i className="fas fa-spin fa-spinner"></i>
              </div>
            )}
            {isSuccess &&
              data.results.map((r: Dataset) => (
                <div key={r.id}>
                  <button className="p-1 border-primary rounded mr-2" onClick={() => addDataset(r)}>
                    <i className="fas fa-plus"></i>
                  </button>
                  {r.title}
                </div>
              ))}
          </div>
        </>
      )}
    </Panel>
  );
}
