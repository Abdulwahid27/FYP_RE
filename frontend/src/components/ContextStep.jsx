import React, { useEffect, useMemo, useState } from "react";
import { api } from "../api.js";
import AuthenticatedImage from "./AuthenticatedImage.jsx";

const OCCASIONS = [
  { id: "social", label: "Social", emoji: "💼", help: "Office or hangouts" },
  { id: "traditional", label: "Traditional", emoji: "🪔", help: "Religious or family gatherings" },
];

const EVENTS_BY_OCCASION = {
  social: [
    { id: "office_wear", label: "Office wear", emoji: "💼" },
    { id: "hangouts", label: "Hangouts", emoji: "☕" },
  ],
  traditional: [
    { id: "religious", label: "Religious", emoji: "🕌" },
    { id: "family_gatherings", label: "Family gatherings", emoji: "🎉" },
  ],
};

const STYLES = [
  { id: "eastern", label: "Eastern", emoji: "🪡" },
  { id: "western", label: "Western", emoji: "👔" },
];

export default function ContextStep({ analysis, onContinue, onBack }) {
  const [gender, setGender] = useState(null);
  const [city, setCity] = useState("");
  const [cities, setCities] = useState([]);
  const [occasion, setOccasion] = useState("social");
  const [eventId, setEventId] = useState("office_wear");
  const [style, setStyle] = useState("eastern");
  const [weather, setWeather] = useState(null);
  const [weatherLoading, setWeatherLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    api.cities().then(setCities).catch(() => {});
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

  const events = useMemo(() => EVENTS_BY_OCCASION[occasion] || [], [occasion]);

  // Whenever the occasion changes, snap the event to the first valid one for it.
  useEffect(() => {
    if (!events.find((e) => e.id === eventId)) {
      setEventId(events[0]?.id || null);
    }
  }, [events, eventId]);

  async function handleContinue() {
    if (!gender) {
      setError("Please pick a gender");
      return;
    }
    if (!city) {
      setError("Please pick a city");
      return;
    }
    if (!eventId) {
      setError("Please pick an event");
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
        event: eventId,
        style,
      });
      onContinue({ gender, city, occasion, event: eventId, style, weather });
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
        <AuthenticatedImage
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
                  aria-pressed={gender === g}
                  className={[
                    "rounded-xl border px-4 py-3 text-sm font-semibold capitalize transition",
                    gender === g
                      ? "bg-ink-900 text-white border-ink-900 shadow-soft"
                      : "bg-white text-ink-500 border-dashed border-ink-300 hover:border-ink-500",
                  ].join(" ")}
                >
                  {g}
                </button>
              ))}
            </div>
            {!gender && (
              <p className="mt-1 text-xs text-ink-400">Please select one to continue.</p>
            )}
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
            <div className="mt-2 grid grid-cols-1 sm:grid-cols-2 gap-3">
              {OCCASIONS.map((o) => (
                <button
                  key={o.id}
                  onClick={() => setOccasion(o.id)}
                  className={[
                    "rounded-xl border px-4 py-4 text-left transition",
                    occasion === o.id
                      ? "bg-accent-500 text-white border-accent-500 shadow-glow"
                      : "bg-white text-ink-700 border-ink-200 hover:border-accent-400",
                  ].join(" ")}
                >
                  <div className="flex items-center gap-2 text-sm font-semibold">
                    <span className="text-xl">{o.emoji}</span>
                    {o.label}
                  </div>
                  <p
                    className={[
                      "text-xs mt-1",
                      occasion === o.id ? "text-white/80" : "text-ink-500",
                    ].join(" ")}
                  >
                    {o.help}
                  </p>
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="field-label">Event</label>
            <div className="mt-2 grid grid-cols-2 gap-3">
              {events.map((ev) => (
                <button
                  key={ev.id}
                  onClick={() => setEventId(ev.id)}
                  className={[
                    "rounded-xl border px-4 py-3 text-sm font-semibold transition flex items-center gap-2 justify-center",
                    eventId === ev.id
                      ? "bg-ink-900 text-white border-ink-900 shadow-soft"
                      : "bg-white text-ink-700 border-ink-200 hover:border-ink-400",
                  ].join(" ")}
                >
                  <span className="text-xl">{ev.emoji}</span>
                  {ev.label}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="field-label">Style</label>
            <div className="mt-2 grid grid-cols-2 gap-3 max-w-md">
              {STYLES.map((s) => (
                <button
                  key={s.id}
                  onClick={() => setStyle(s.id)}
                  className={[
                    "rounded-xl border px-4 py-3 text-sm font-semibold transition flex items-center gap-2 justify-center",
                    style === s.id
                      ? "bg-ink-900 text-white border-ink-900 shadow-soft"
                      : "bg-white text-ink-700 border-ink-200 hover:border-ink-400",
                  ].join(" ")}
                >
                  <span className="text-xl">{s.emoji}</span>
                  {s.label}
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
