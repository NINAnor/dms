import React, { useState, useEffect } from "https://esm.sh/react@18";
import { createRoot } from "https://esm.sh/react-dom@18/client";
import { HighTable, createEventTarget } from "https://esm.sh/hightable";
import {
  byteLengthFromUrl,
  parquetMetadataAsync,
  asyncBufferFromUrl,
  parquetReadObjects,
} from "https://esm.sh/hyparquet";

import { compressors } from "https://esm.sh/hyparquet-compressors";

const root = document.getElementById("parquet-preview");
const eventTarget = createEventTarget();

async function load(url) {
  const byteLenght = await byteLengthFromUrl(url);
  const asyncBuffer = await asyncBufferFromUrl({ url, byteLenght });
  const metadata = await parquetMetadataAsync(asyncBuffer);
  console.log("Metadata:", metadata);

  const header = metadata.schema
    .filter((field) => field.type)
    .map((field) => field.name);
  const cellCache = new Map(header.map((column) => [column, []]));

  return {
    eventTarget,
    numRows: Number(metadata.num_rows),
    header,
    getRowNumber: ({ row }) => {
      return row;
    },
    getCell: ({ row, column }) => {
      return { value: cellCache.get(column)[row] };
    },
    async fetch({ rowStart, rowEnd, columns }) {
      const rows = await parquetReadObjects({
        file: asyncBuffer,
        columns,
        rowStart,
        rowEnd,
        compressors,
      });
      let rowNumber = rowStart;
      for (const row of rows) {
        for (const column of columns) {
          cellCache.get(column)[rowNumber] = row[column];
        }
        eventTarget.dispatchEvent(new CustomEvent("resolve"));
        rowNumber++;
      }
    },
  };
}

function App() {
  const [data, setData] = useState(null);
  const [error, setError] = useState();

  useEffect(() => {
    load(root.getAttribute("data-url")).then((d) => setData(d));
  }, []);

  if (!data) {
    return <div>Loading...</div>;
  }

  return <HighTable data={data} setError={setError} />;
}

createRoot(root).render(<App />);
