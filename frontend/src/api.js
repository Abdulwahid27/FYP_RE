const BASE = import.meta.env.VITE_API_BASE || "";

async function asJson(res) {
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const data = await res.json();
      detail = data?.detail || JSON.stringify(data);
    } catch {}
    throw new Error(detail || `Request failed (${res.status})`);
  }
  return res.json();
}

export const api = {
  async analyze(file, { signal } = {}) {
    const fd = new FormData();
    fd.append("file", file);
    const res = await fetch(`${BASE}/api/analyze`, {
      method: "POST",
      body: fd,
      signal,
    });
    return asJson(res);
  },

  async cities() {
    const res = await fetch(`${BASE}/api/cities`);
    return asJson(res);
  },

  async weather(city) {
    const res = await fetch(`${BASE}/api/weather?city=${encodeURIComponent(city)}`);
    return asJson(res);
  },

  async setContext(payload) {
    const res = await fetch(`${BASE}/api/context`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    return asJson(res);
  },

  async brands() {
    const res = await fetch(`${BASE}/api/brands`);
    return asJson(res);
  },

  async garments({ gender, occasion, brandId } = {}) {
    const params = new URLSearchParams({ gender, occasion });
    if (brandId) params.set("brand_id", brandId);
    const res = await fetch(`${BASE}/api/garments?${params.toString()}`);
    return asJson(res);
  },

  async tryon({ session_id, garment_id }) {
    const res = await fetch(`${BASE}/api/tryon`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id, garment_id }),
    });
    return asJson(res);
  },

  async sessions() {
    const res = await fetch(`${BASE}/api/sessions`);
    return asJson(res);
  },
};
