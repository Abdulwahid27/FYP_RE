import React, { useEffect, useState } from "react";
import { api, authHeaders } from "../api.js";
import AuthenticatedImage from "./AuthenticatedImage.jsx";

const BASE = import.meta.env.VITE_API_BASE || "";

const EVENT_LABELS = {
  office_wear: "Office wear",
  hangouts: "Hangouts",
  religious: "Religious",
  family_gatherings: "Family gatherings",
};

function formatWhen(iso) {
  if (!iso) return "";
  try {
    return new Date(iso).toLocaleString(undefined, {
      dateStyle: "medium",
      timeStyle: "short",
    });
  } catch {
    return iso;
  }
}

function contextLine(s) {
  const parts = [];
  if (s.city) parts.push(s.city);
  if (s.event && EVENT_LABELS[s.event]) parts.push(EVENT_LABELS[s.event]);
  else if (s.event) parts.push(s.event);
  if (s.occasion) parts.push(s.occasion);
  return parts.join(" · ");
}

export default function MyLooksStep({ onBack, onNewSession }) {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selected, setSelected] = useState(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    api
      .sessions()
      .then((rows) => {
        if (cancelled) return;
        const withTryon = (rows || []).filter((s) => s.tryon_url);
        setItems(withTryon);
        setSelected(withTryon[0] ?? null);
      })
      .catch((e) => {
        if (!cancelled) setError(e.message || "Could not load your looks.");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  async function handleSave(tryonUrl, sessionId) {
    const path = tryonUrl.startsWith("http") ? tryonUrl : `${BASE}${tryonUrl}`;
    const res = await fetch(path, { headers: { ...authHeaders() }, cache: "no-store" });
    if (!res.ok) throw new Error("Could not download");
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `atelier-look-${sessionId}.png`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  }

  return (
    <section className="fade-in space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-4">
        <div>
          <p className="field-label">Your wardrobe</p>
          <h2
            className="font-display text-3xl mt-1 text-[#f3ede3]"
            style={{ fontFamily: "'Cormorant Garamond', Georgia, serif" }}
          >
            My looks
          </h2>
          <p className="text-sm text-[#a89b8c] mt-2 max-w-xl">
            Saved try-ons from your account only. Other members cannot see these images.
          </p>
        </div>
        <div className="flex gap-2 flex-wrap">
          <button type="button" className="btn-ghost text-xs" onClick={onBack}>
            ← Back to studio
          </button>
          <button type="button" className="btn-primary text-xs" onClick={onNewSession}>
            New fitting
          </button>
        </div>
      </div>

      {loading && (
        <div className="card p-10 text-center text-[#a89b8c] text-sm">Loading your looks…</div>
      )}

      {error && (
        <div className="card p-6 border border-accent-500/30 text-accent-200 text-sm">{error}</div>
      )}

      {!loading && !error && items.length === 0 && (
        <div className="card p-10 text-center">
          <p className="text-[#e8e2d9] font-medium">No saved try-ons yet</p>
          <p className="text-sm text-[#a89b8c] mt-2">
            Complete a fitting in the studio and your result will appear here.
          </p>
          <button type="button" className="btn-primary mt-6" onClick={onNewSession}>
            Start a fitting
          </button>
        </div>
      )}

      {!loading && !error && items.length > 0 && (
        <div className="grid lg:grid-cols-[minmax(0,1fr)_minmax(280px,360px)] gap-6 items-start">
          <div className="grid sm:grid-cols-2 xl:grid-cols-3 gap-4">
            {items.map((s) => {
              const active = selected?.id === s.id;
              return (
                <button
                  key={s.id}
                  type="button"
                  onClick={() => setSelected(s)}
                  className={[
                    "card p-3 text-left transition ring-1",
                    active
                      ? "ring-[#c9a25c]/60 shadow-lg"
                      : "ring-transparent hover:ring-white/15",
                  ].join(" ")}
                >
                  <div className="aspect-[3/4] rounded-xl overflow-hidden bg-ink-900/40 border border-white/10">
                    <AuthenticatedImage
                      key={s.tryon_url}
                      src={s.tryon_url}
                      alt={s.garment_title || "Try-on"}
                      className="w-full h-full object-cover"
                    />
                  </div>
                  <p className="mt-3 text-sm font-semibold text-[#f3ede3] line-clamp-1">
                    {s.garment_title || "Saved look"}
                  </p>
                  <p className="text-[11px] text-[#a89b8c] mt-0.5">{formatWhen(s.created_at)}</p>
                  {contextLine(s) && (
                    <p className="text-[11px] text-[#8a7f72] mt-1 line-clamp-2">{contextLine(s)}</p>
                  )}
                </button>
              );
            })}
          </div>

          {selected && (
            <div className="card p-5 lg:sticky lg:top-24 space-y-4">
              <p className="field-label">Selected look</p>
              <div className="rounded-2xl overflow-hidden border border-white/10">
                <AuthenticatedImage
                  key={`detail-${selected.tryon_url}`}
                  src={selected.tryon_url}
                  alt="Selected try-on"
                  className="w-full max-h-[520px] object-contain bg-black/30"
                />
              </div>
              <div className="space-y-1 text-sm">
                {selected.garment_brand && (
                  <p className="text-[#a89b8c] text-xs uppercase tracking-wider">
                    {selected.garment_brand}
                  </p>
                )}
                <p className="font-semibold text-[#f3ede3]">
                  {selected.garment_title || "Garment"}
                </p>
                <p className="text-[#a89b8c] text-xs">{formatWhen(selected.created_at)}</p>
                {contextLine(selected) && (
                  <p className="text-[#8a7f72] text-xs">{contextLine(selected)}</p>
                )}
                {(selected.skin_tone || selected.face_shape) && (
                  <p className="text-[#8a7f72] text-xs pt-1">
                    {[selected.skin_tone, selected.face_shape].filter(Boolean).join(" · ")}
                  </p>
                )}
              </div>
              <button
                type="button"
                className="btn-accent w-full"
                onClick={() => handleSave(selected.tryon_url, selected.id).catch(() => {})}
              >
                ↓ Save image
              </button>
            </div>
          )}
        </div>
      )}
    </section>
  );
}
