import React from "react";

export default function ResultStep({ result, garment, onRestart, onPickAnother }) {
  async function handleSave() {
    try {
      const res = await fetch(result.tryon_url);
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `atelier-tryon-${result.session_id}.png`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
    } catch {
      window.open(result.tryon_url, "_blank");
    }
  }

  return (
    <section className="fade-in grid lg:grid-cols-3 gap-8 items-start">
      <div className="card p-4 lg:col-span-2 bg-hero-radial">
        <div className="rounded-2xl overflow-hidden bg-white border border-ink-100">
          <img
            src={result.tryon_url}
            alt="Your virtual try-on"
            className="w-full max-h-[720px] object-contain"
          />
        </div>
      </div>

      <div className="card p-6 space-y-5">
        <div>
          <p className="field-label">Step 5 · The reveal</p>
          <h2 className="font-display text-3xl mt-1">Your styled look</h2>
          <p className="text-ink-500 text-sm mt-2">
            Save it for later, share it with friends, or try a different piece —
            your studio is open.
          </p>
        </div>

        <div className="rounded-2xl bg-ink-50 border border-ink-100 p-4">
          <p className="field-label">Garment</p>
          <p className="mt-1 font-semibold">{garment.title}</p>
          <p className="text-xs text-ink-500 mt-1">
            {garment.color ? `${garment.color} · ` : ""}
            {garment.price || ""}
          </p>
        </div>

        <div className="grid grid-cols-2 gap-3">
          <a
            href={result.garment_extracted_url}
            target="_blank"
            rel="noreferrer"
            className="rounded-xl border border-ink-100 p-3 hover:border-ink-400 transition"
          >
            <p className="field-label">Extracted</p>
            <div className="mt-2 aspect-square rounded-lg tryon-frame overflow-hidden">
              <img
                src={result.garment_extracted_url}
                alt="Extracted garment"
                className="w-full h-full object-contain"
              />
            </div>
          </a>
          <a
            href={result.tryon_url}
            target="_blank"
            rel="noreferrer"
            className="rounded-xl border border-ink-100 p-3 hover:border-ink-400 transition"
          >
            <p className="field-label">Final</p>
            <div className="mt-2 aspect-square rounded-lg overflow-hidden bg-ink-50">
              <img
                src={result.tryon_url}
                alt="Final"
                className="w-full h-full object-cover"
              />
            </div>
          </a>
        </div>

        <div className="flex flex-col gap-3">
          <button className="btn-accent w-full" onClick={handleSave}>
            ↓ Save look
          </button>
          <button className="btn-primary w-full" onClick={onPickAnother}>
            Try another piece
          </button>
          <button className="btn-ghost w-full" onClick={onRestart}>
            Start over
          </button>
        </div>
      </div>
    </section>
  );
}
