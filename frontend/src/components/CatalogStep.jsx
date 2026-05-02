import React, { useEffect, useMemo, useState } from "react";
import { api } from "../api.js";

export function garmentImageSrc(g) {
  return `/api/garments/${g.id}/image`;
}

export default function CatalogStep({ context, brands, onPick, onBack }) {
  const [garments, setGarments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeBrandId, setActiveBrandId] = useState(context.brandId || null);

  useEffect(() => {
    setLoading(true);
    api
      .garments({
        gender: context.gender,
        occasion: context.occasion,
        brandId: activeBrandId,
      })
      .then((g) => setGarments(g))
      .catch(() => setGarments([]))
      .finally(() => setLoading(false));
  }, [context.gender, context.occasion, activeBrandId]);

  const brandsById = useMemo(
    () => Object.fromEntries(brands.map((b) => [b.id, b])),
    [brands]
  );

  return (
    <section className="fade-in space-y-6">
      <div className="card p-6 flex flex-wrap items-center justify-between gap-4">
        <div>
          <p className="field-label">Step 3</p>
          <h2 className="font-display text-3xl mt-1">Curated for you</h2>
          <p className="text-ink-500 text-sm mt-1">
            <span className="capitalize">{context.gender}</span> ·{" "}
            <span className="capitalize">{context.occasion}</span>
            {context.city && <> · {context.city}</>}
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <button
            className={[
              "chip",
              !activeBrandId
                ? "border-ink-900 bg-ink-900 text-white"
                : "border-ink-200 bg-white text-ink-700 hover:border-ink-400",
            ].join(" ")}
            onClick={() => setActiveBrandId(null)}
          >
            All brands
          </button>
          {brands.map((b) => (
            <button
              key={b.id}
              className={[
                "chip",
                activeBrandId === b.id
                  ? "border-ink-900 bg-ink-900 text-white"
                  : "border-ink-200 bg-white text-ink-700 hover:border-ink-400",
              ].join(" ")}
              onClick={() => setActiveBrandId(b.id)}
            >
              {b.name}
            </button>
          ))}
        </div>
      </div>

      {loading ? (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-5">
          {Array.from({ length: 8 }).map((_, i) => (
            <div key={i} className="card overflow-hidden">
              <div className="aspect-[3/4] bg-ink-100 shimmer" />
              <div className="p-4 space-y-2">
                <div className="h-3 w-2/3 bg-ink-100 rounded" />
                <div className="h-3 w-1/3 bg-ink-100 rounded" />
              </div>
            </div>
          ))}
        </div>
      ) : garments.length === 0 ? (
        <div className="card p-10 text-center text-ink-500">
          <p className="font-display text-xl">No looks found yet</p>
          <p className="text-sm mt-1">
            Try a different brand or occasion to see more.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-5">
          {garments.map((g) => (
            <article
              key={g.id}
              className="card overflow-hidden group hover:shadow-glow transition cursor-pointer"
              onClick={() => onPick(g)}
            >
              <div className="aspect-[3/4] overflow-hidden bg-ink-50">
                <img
                  src={garmentImageSrc(g)}
                  alt={g.title}
                  loading="lazy"
                  className="w-full h-full object-cover group-hover:scale-[1.04] transition"
                />
              </div>
              <div className="p-4">
                <p className="text-xs text-ink-400 uppercase tracking-wider">
                  {brandsById[g.brand_id]?.name || "Brand"}
                </p>
                <h3 className="text-sm font-semibold mt-1 line-clamp-2">{g.title}</h3>
                <div className="mt-2 flex items-center justify-between">
                  <span className="text-xs text-ink-500">{g.color || ""}</span>
                  <span className="text-xs font-semibold text-ink-900">
                    {g.price || ""}
                  </span>
                </div>
                <button
                  className="mt-4 w-full btn-primary text-xs py-2"
                  onClick={(e) => {
                    e.stopPropagation();
                    onPick(g);
                  }}
                >
                  Try this on
                </button>
              </div>
            </article>
          ))}
        </div>
      )}

      <div className="flex">
        <button className="btn-ghost" onClick={onBack}>
          ← Edit context
        </button>
      </div>
    </section>
  );
}
