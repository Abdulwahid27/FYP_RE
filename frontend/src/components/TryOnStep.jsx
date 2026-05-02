import React, { useEffect, useRef, useState } from "react";
import { api } from "../api.js";
import { garmentImageSrc } from "./CatalogStep.jsx";

const STAGES = [
  "Reading your photo",
  "Lifting the garment from the catalog",
  "Tailoring the fit to your portrait",
  "Polishing the final look",
];

export default function TryOnStep({ analysis, garment, onDone, onBack }) {
  const [stageIdx, setStageIdx] = useState(0);
  const [error, setError] = useState(null);
  const [done, setDone] = useState(false);
  const startedRef = useRef(false);
  const onDoneRef = useRef(onDone);
  onDoneRef.current = onDone;

  useEffect(() => {
    if (startedRef.current) return;
    startedRef.current = true;

    let alive = true;
    let timer = null;
    const advance = () => {
      timer = setInterval(() => {
        setStageIdx((i) => Math.min(i + 1, STAGES.length - 1));
      }, 6000);
    };
    advance();

    (async () => {
      try {
        const res = await api.tryon({
          session_id: analysis.session_id,
          garment_id: garment.id,
        });
        if (!alive) return;
        setStageIdx(STAGES.length - 1);
        setDone(true);
        clearInterval(timer);
        onDoneRef.current(res);
      } catch (e) {
        if (!alive) return;
        setError(e.message);
        clearInterval(timer);
      }
    })();

    return () => {
      alive = false;
      if (timer) clearInterval(timer);
      // React 18 Strict Mode remounts; allow the second mount to start try-on
      startedRef.current = false;
    };
  }, [analysis.session_id, garment.id]);

  return (
    <section className="fade-in grid lg:grid-cols-2 gap-8 items-stretch">
      <div className="card p-6">
        <p className="field-label">Step 4</p>
        <h2 className="font-display text-3xl mt-1">Crafting your look</h2>
        <p className="text-ink-500 text-sm mt-2">
          Hang tight — we're hand-stitching this just for you. This usually
          takes 30–90 seconds.
        </p>

        <div className="mt-6 grid grid-cols-2 gap-4">
          <Preview label="Your portrait" src={analysis.portrait_url} />
          <Preview label="Selected look" src={garmentImageSrc(garment)} />
        </div>

        <ol className="mt-6 space-y-3">
          {STAGES.map((s, i) => {
            const status =
              i < stageIdx ? "done" : i === stageIdx ? "active" : "pending";
            return (
              <li key={i} className="flex items-center gap-3">
                <span
                  className={[
                    "h-6 w-6 rounded-full flex items-center justify-center text-[10px] font-bold",
                    status === "done" && "bg-ink-900 text-white",
                    status === "active" && "bg-accent-500 text-white animate-pulse",
                    status === "pending" && "bg-ink-100 text-ink-400",
                  ]
                    .filter(Boolean)
                    .join(" ")}
                >
                  {status === "done" ? "✓" : i + 1}
                </span>
                <span
                  className={[
                    "text-sm",
                    status === "pending" ? "text-ink-400" : "text-ink-800",
                  ].join(" ")}
                >
                  {s}
                </span>
              </li>
            );
          })}
        </ol>

        {error && (
          <div className="mt-6 rounded-xl bg-accent-50 border border-accent-200 p-4 text-sm text-accent-700">
            <p className="font-semibold">Couldn't finish the fitting.</p>
            <p className="mt-1">{error}</p>
            <button className="btn-ghost mt-3" onClick={onBack}>
              ← Pick a different look
            </button>
          </div>
        )}
      </div>

      <div className="card p-6 flex items-center justify-center min-h-[420px] bg-hero-radial">
        <div className="w-full max-w-md aspect-[3/4] rounded-2xl tryon-frame relative overflow-hidden border border-ink-100">
          <div className="absolute inset-0 flex items-center justify-center">
            {!done && !error && (
              <div className="text-center">
                <div className="h-12 w-12 mx-auto rounded-full border-4 border-accent-500 border-t-transparent animate-spin" />
                <p className="mt-4 font-display text-lg text-ink-700">
                  Tailoring in progress…
                </p>
              </div>
            )}
            {error && (
              <div className="text-center text-ink-500 text-sm">
                Fitting cancelled.
              </div>
            )}
          </div>
        </div>
      </div>
    </section>
  );
}

function Preview({ label, src }) {
  return (
    <div>
      <p className="field-label">{label}</p>
      <div className="mt-2 aspect-[3/4] rounded-xl overflow-hidden bg-ink-50 border border-ink-100">
        <img src={src} alt={label} className="w-full h-full object-cover" />
      </div>
    </div>
  );
}
