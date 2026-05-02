import React, { useEffect, useState } from "react";
import { api } from "../api.js";

const OCCASIONS = [
  { id: "wedding", label: "Wedding", emoji: "💍" },
  { id: "casual", label: "Casual", emoji: "☕" },
  { id: "office", label: "Office", emoji: "💼" },
  { id: "party", label: "Party", emoji: "✨" },
];

export default function ContextStep({ analysis, onContinue, onBack }) {
  const [gender, setGender] = useState("female");
  const [city, setCity] = useState("");
  const [cities, setCities] = useState([]);
  const [occasion, setOccasion] = useState("casual");
  const [brands, setBrands] = useState([]);
  const [brandId, setBrandId] = useState(null);
  const [weather, setWeather] = useState(null);
  const [weatherLoading, setWeatherLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    api.cities().then(setCities).catch(() => {});
    api.brands().then(setBrands).catch(() => {});
  }, []);

  useEffect(() => {
    if (!city) {
      setWeather(null);
      return;
    }
    setWeatherLoading(true);
    api
      .weather(city)
      .then(setWeather)
      .catch(() => setWeather(null))
      .finally(() => setWeatherLoading(false));
  }, [city]);

  async function handleContinue() {
    if (!city) {
      setError("Please pick a city");
      return;
    }
    setSubmitting(true);
    setError(null);
    try {
      await api.setContext({
        session_id: analysis.session_id,
        gender,
        city,
        occasion,
        brand_id: brandId || null,
      });
      onContinue({ gender, city, occasion, brandId, weather });
    } catch (e) {
      setError(e.message);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <section className="grid lg:grid-cols-3 gap-8 fade-in">
      <div className="card p-6 lg:col-span-1">
        <p className="field-label">Your portrait</p>
        <img
          src={analysis.portrait_url}
          alt="portrait"
          className="mt-3 w-full max-h-[420px] object-contain rounded-2xl shadow-soft bg-ink-50"
        />
        <div className="mt-5 grid grid-cols-2 gap-3">
          <Insight label="Skin tone" value={analysis.skin_tone || "—"} />
          <Insight label="Face shape" value={analysis.face_shape || "—"} />
        </div>
      </div>

      <div className="card p-8 lg:col-span-2">
        <p className="field-label">Step 2</p>
        <h2 className="font-display text-3xl mt-2">Tell us a little more</h2>
        <p className="text-ink-500 text-sm mt-2">
          We use these details — plus today's weather — to curate the right
          looks.
        </p>

        <div className="mt-6 space-y-6">
          <div>
            <label className="field-label">Gender</label>
            <div className="mt-2 grid grid-cols-2 gap-3 max-w-xs">
              {["female", "male"].map((g) => (
                <button
                  key={g}
                  onClick={() => setGender(g)}
                  className={[
                    "rounded-xl border px-4 py-3 text-sm font-semibold capitalize transition",
                    gender === g
                      ? "bg-ink-900 text-white border-ink-900 shadow-soft"
                      : "bg-white text-ink-700 border-ink-200 hover:border-ink-400",
                  ].join(" ")}
                >
                  {g}
                </button>
              ))}
            </div>
          </div>

          <div className="grid sm:grid-cols-2 gap-4">
            <div>
              <label className="field-label">Location</label>
              <select
                className="input mt-2"
                value={city}
                onChange={(e) => setCity(e.target.value)}
              >
                <option value="">Select a city…</option>
                {cities.map((c) => (
                  <option key={c.name} value={c.name}>
                    {c.label}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="field-label">Today's weather</label>
              <div className="mt-2 input min-h-[44px] flex items-center gap-3 bg-ink-50">
                {!city && (
                  <span className="text-ink-400 text-sm">Pick a city first</span>
                )}
                {city && weatherLoading && (
                  <span className="text-ink-400 text-sm">Checking…</span>
                )}
                {weather && !weatherLoading && (
                  <>
                    {weather.icon && (
                      <img
                        src={`https://openweathermap.org/img/wn/${weather.icon}@2x.png`}
                        alt=""
                        className="h-9 w-9"
                      />
                    )}
                    <div className="text-sm">
                      <span className="font-semibold">
                        {Math.round(weather.temperature_c)}°C
                      </span>
                      <span className="text-ink-500 ml-2 capitalize">
                        {weather.description}
                      </span>
                    </div>
                  </>
                )}
              </div>
            </div>
          </div>

          <div>
            <label className="field-label">Occasion</label>
            <div className="mt-2 grid grid-cols-2 sm:grid-cols-4 gap-3">
              {OCCASIONS.map((o) => (
                <button
                  key={o.id}
                  onClick={() => setOccasion(o.id)}
                  className={[
                    "rounded-xl border px-4 py-3 text-sm font-semibold transition flex flex-col items-center gap-1",
                    occasion === o.id
                      ? "bg-accent-500 text-white border-accent-500 shadow-glow"
                      : "bg-white text-ink-700 border-ink-200 hover:border-accent-400",
                  ].join(" ")}
                >
                  <span className="text-xl">{o.emoji}</span>
                  {o.label}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="field-label">Preferred brand (optional)</label>
            <div className="mt-2 flex flex-wrap gap-2">
              <button
                onClick={() => setBrandId(null)}
                className={[
                  "chip",
                  !brandId
                    ? "border-ink-900 bg-ink-900 text-white"
                    : "border-ink-200 bg-white text-ink-700 hover:border-ink-400",
                ].join(" ")}
              >
                Any brand
              </button>
              {brands.map((b) => (
                <button
                  key={b.id}
                  onClick={() => setBrandId(b.id)}
                  className={[
                    "chip",
                    brandId === b.id
                      ? "border-ink-900 bg-ink-900 text-white"
                      : "border-ink-200 bg-white text-ink-700 hover:border-ink-400",
                  ].join(" ")}
                  title={b.description || b.name}
                >
                  {b.name}
                </button>
              ))}
            </div>
          </div>

          {error && (
            <p className="text-sm text-accent-700 bg-accent-50 border border-accent-200 rounded-xl px-4 py-2">
              {error}
            </p>
          )}

          <div className="flex gap-3 pt-2">
            <button className="btn-ghost" onClick={onBack}>
              ← Back
            </button>
            <button
              className="btn-accent"
              onClick={handleContinue}
              disabled={submitting}
            >
              {submitting ? "Saving…" : "Browse the catalog →"}
            </button>
          </div>
        </div>
      </div>
    </section>
  );
}

function Insight({ label, value }) {
  return (
    <div className="rounded-2xl bg-ink-50 border border-ink-100 p-4">
      <p className="field-label">{label}</p>
      <p className="mt-1 capitalize text-ink-900 font-semibold">{value}</p>
    </div>
  );
}
