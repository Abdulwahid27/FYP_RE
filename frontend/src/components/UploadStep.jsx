import React, { useRef, useState } from "react";
import { api } from "../api.js";

export default function UploadStep({ onAnalyzed }) {
  const inputRef = useRef(null);
  const abortRef = useRef(null);
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  function pick(f) {
    if (!f) return;
    setFile(f);
    setPreview(URL.createObjectURL(f));
    setError(null);
  }

  async function handleAnalyze() {
    if (!file) return;
    const ctrl = new AbortController();
    abortRef.current = ctrl;
    setLoading(true);
    setError(null);
    try {
      const data = await api.analyze(file, { signal: ctrl.signal });
      onAnalyzed(data);
    } catch (e) {
      if (e.name === "AbortError") {
        setError("Analysis stopped.");
      } else {
        setError(e.message);
      }
    } finally {
      setLoading(false);
      abortRef.current = null;
    }
  }

  function handleStop() {
    abortRef.current?.abort();
  }

  return (
    <section className="grid lg:grid-cols-2 gap-8 fade-in">
      <div className="card p-8">
        <p className="field-label">Step 1</p>
        <h2 className="font-display text-3xl mt-2">Upload your portrait</h2>
        <p className="text-ink-500 mt-2 text-sm leading-relaxed">
          A clear, front-facing photo gives the best results. We'll quietly study
          your skin tone and face shape to tailor recommendations — your image
          stays private and is only used for this session.
        </p>

        <div
          className="mt-6 border-2 border-dashed border-ink-200 rounded-2xl p-8 text-center hover:border-accent-400 transition cursor-pointer bg-white/40"
          onClick={() => inputRef.current?.click()}
          onDragOver={(e) => e.preventDefault()}
          onDrop={(e) => {
            e.preventDefault();
            const f = e.dataTransfer.files?.[0];
            pick(f);
          }}
        >
          <input
            ref={inputRef}
            type="file"
            accept="image/*"
            className="hidden"
            onChange={(e) => pick(e.target.files?.[0])}
          />
          <div className="text-4xl">📸</div>
          <p className="mt-3 text-sm font-semibold text-ink-700">
            Click or drag & drop a portrait
          </p>
          <p className="text-xs text-ink-400 mt-1">JPG, PNG, or WEBP — up to ~10MB</p>
        </div>

        {error && (
          <p className="mt-4 text-sm text-accent-700 bg-accent-50 border border-accent-200 rounded-xl px-4 py-2">
            {error}
          </p>
        )}

        <div className="mt-6 flex gap-3">
          <button
            className="btn-accent"
            onClick={handleAnalyze}
            disabled={!file || loading}
          >
            {loading ? (
              <>
                <span className="h-3 w-3 rounded-full bg-white animate-pulse" />
                Studying your features…
              </>
            ) : (
              <>Analyze portrait →</>
            )}
          </button>
          {loading && (
            <button
              className="btn-ghost text-accent-700 border-accent-200 hover:border-accent-400"
              onClick={handleStop}
            >
              ■ Stop
            </button>
          )}
          {file && !loading && (
            <button
              className="btn-ghost"
              onClick={() => {
                setFile(null);
                setPreview(null);
                setError(null);
              }}
            >
              Clear
            </button>
          )}
        </div>
      </div>

      <div className="card p-4 lg:p-6 flex items-center justify-center min-h-[360px] bg-hero-radial">
        {preview ? (
          <div className="relative w-full">
            <img
              src={preview}
              alt="preview"
              className="w-full max-h-[520px] object-contain rounded-2xl shadow-soft"
            />
            {loading && (
              <div className="absolute inset-0 rounded-2xl overflow-hidden">
                <div className="absolute inset-0 bg-white/40 backdrop-blur-[2px]" />
                <div className="absolute inset-0 shimmer" />
              </div>
            )}
          </div>
        ) : (
          <div className="text-center text-ink-400">
            <div className="text-7xl">🪞</div>
            <p className="mt-4 font-display text-2xl text-ink-700">
              Your studio mirror
            </p>
            <p className="text-sm text-ink-400 mt-1">
              Drop a portrait on the left to begin.
            </p>
          </div>
        )}
      </div>
    </section>
  );
}
