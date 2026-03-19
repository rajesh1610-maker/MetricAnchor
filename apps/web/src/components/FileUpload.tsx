"use client";

import { useCallback, useState } from "react";
import { uploadDataset, type Dataset } from "@/lib/api";

interface Props {
  onSuccess: (dataset: Dataset) => void;
}

export default function FileUpload({ onSuccess }: Props) {
  const [dragging, setDragging] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState<"idle" | "uploading" | "error">("idle");
  const [error, setError] = useState<string | null>(null);

  const handleFile = useCallback((f: File) => {
    setFile(f);
    setError(null);
    setStatus("idle");
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setDragging(false);
      const f = e.dataTransfer.files[0];
      if (f) handleFile(f);
    },
    [handleFile]
  );

  const handleChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const f = e.target.files?.[0];
      if (f) handleFile(f);
    },
    [handleFile]
  );

  const handleUpload = async () => {
    if (!file) return;
    setStatus("uploading");
    setError(null);
    try {
      const dataset = await uploadDataset(file);
      onSuccess(dataset);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed.");
      setStatus("error");
    }
  };

  const formatBytes = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1_048_576) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / 1_048_576).toFixed(1)} MB`;
  };

  return (
    <div className="space-y-4">
      {/* Drop zone */}
      <label
        onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={handleDrop}
        className={`flex cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed p-12 transition-colors ${
          dragging
            ? "border-anchor-500 bg-anchor-50"
            : "border-gray-200 bg-gray-50 hover:border-anchor-300 hover:bg-anchor-50/50"
        }`}
      >
        <input
          type="file"
          accept=".csv,.parquet"
          className="sr-only"
          onChange={handleChange}
        />
        <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-white shadow-sm">
          <svg className="h-7 w-7 text-anchor-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
              d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5" />
          </svg>
        </div>
        {file ? (
          <div className="text-center">
            <p className="font-medium text-gray-900">{file.name}</p>
            <p className="text-sm text-gray-400">{formatBytes(file.size)}</p>
          </div>
        ) : (
          <div className="text-center">
            <p className="font-medium text-gray-700">Drop a file here, or click to browse</p>
            <p className="mt-1 text-sm text-gray-400">CSV and Parquet · max 500 MB</p>
          </div>
        )}
      </label>

      {/* Error */}
      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {error}
        </div>
      )}

      {/* Upload button */}
      <button
        onClick={handleUpload}
        disabled={!file || status === "uploading"}
        className="w-full rounded-lg bg-anchor-600 px-6 py-3 text-sm font-semibold text-white shadow-sm transition-colors hover:bg-anchor-700 disabled:cursor-not-allowed disabled:opacity-50"
      >
        {status === "uploading" ? (
          <span className="flex items-center justify-center gap-2">
            <svg className="h-4 w-4 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
            Uploading and profiling…
          </span>
        ) : (
          "Upload Dataset"
        )}
      </button>
    </div>
  );
}
