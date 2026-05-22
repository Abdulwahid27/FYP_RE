import React from "react";
import { authHeaders } from "../api.js";
import AuthenticatedImage from "./AuthenticatedImage.jsx";

const BASE = import.meta.env.VITE_API_BASE || "";

function publicAssetUrl(path) {
  if (!path) return "";
  if (path.startsWith("http")) return path;
  return `${BASE}${path}`;
}

export default function ResultStep({ result, garment, onRestart, onPickAnother, onViewHistory }) {
  async function fetchTryonBlob() {
    const path = result.tryon_url.startsWith("http") ? result.tryon_url : `${BASE}${result.tryon_url}`;
    const res = await fetch(path, { headers: { ...authHeaders() }, cache: "no-store" });
    if (!res.ok) throw new Error("Could not load try-on");
    return res.blob();
  }

  async function handleSave() {
    try {
      const blob = await fetchTryonBlob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `atelier-tryon-${result.session_id}.png`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
    } catch {
      /* AuthenticatedImage still shows preview */
    }
  }

  async function openTryonInNewTab() {
    try {
      const blob = await fetchTryonBlob();
      const url = URL.createObjectURL(blob);
      const w = window.open(url, "_blank");
      if (w) {
        setTimeout(() => URL.revokeObjectURL(url), 120_000);
      } else {
        URL.revokeObjectURL(url);
      }
    } catch {
      /* ignore */
    }
  }

  return (
    <section className="fade-in grid lg:grid-cols-3 gap-8 items-start">
      <div className="card p-4 lg:col-span-2 bg-hero-radial">
        <div className="rounded-2xl overflow-hidden bg-white border border-ink-100">
          <AuthenticatedImage
            key={`${result.tryon_url}-${garment.id}`}
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
            Save it for later, share it with friends, or try a different piece — your studio is open.
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
            href={publicAssetUrl(result.garment_extracted_url)}
            target="_blank"
            rel="noreferrer"
            className="rounded-xl border border-ink-100 p-3 hover:border-ink-400 transition"
          >
            <p className="field-label">Extracted</p>
            <div className="mt-2 aspect-square rounded-lg tryon-frame overflow-hidden">
              <img
                src={publicAssetUrl(result.garment_extracted_url)}
                alt="Extracted garment"
                className="w-full h-full object-contain"
              />
            </div>
          </a>
          <button
            type="button"
            onClick={openTryonInNewTab}
            className="rounded-xl border border-ink-100 p-3 hover:border-ink-400 transition text-left w-full"
          >
            <p className="field-label">Final</p>
            <div className="mt-2 aspect-square rounded-lg overflow-hidden bg-ink-50">
              <AuthenticatedImage
                key={`thumb-${result.tryon_url}-${garment.id}`}
                src={result.tryon_url}
                alt="Final"
                className="w-full h-full object-cover"
              />
            </div>
          </button>
        </div>

        <div className="flex flex-col gap-3">
          <button className="btn-accent w-full" onClick={handleSave}>
            ↓ Save look
          </button>
          <button className="btn-primary w-full" onClick={onPickAnother}>
            Try another piece
          </button>
          {onViewHistory && (
            <button type="button" className="btn-ghost w-full" onClick={onViewHistory}>
              View all my looks
            </button>
          )}
          <button className="btn-ghost w-full" onClick={onRestart}>
            Start over
          </button>
        </div>
      </div>
    </section>
  );
}
