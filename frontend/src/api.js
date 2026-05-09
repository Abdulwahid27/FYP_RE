const BASE = import.meta.env.VITE_API_BASE || "";

const TOKEN_KEY = "atelier_token";

export function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token) {
  if (token) localStorage.setItem(TOKEN_KEY, token);
  else localStorage.removeItem(TOKEN_KEY);
}

export function authHeaders() {
  const t = getToken();
  return t ? { Authorization: `Bearer ${t}` } : {};
}

async function asJson(res) {
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const data = await res.json();
      detail = data?.detail ?? data?.message;
      if (Array.isArray(detail)) {
        detail = detail.map((d) => (typeof d === "string" ? d : d?.msg || JSON.stringify(d))).join(" · ");
      }
      if (typeof detail !== "string") detail = detail != null ? JSON.stringify(detail) : res.statusText;
    } catch {
      /* keep detail */
    }
    throw new Error(detail || `Request failed (${res.status})`);
  }
  return res.json();
}

export const api = {
  async register({ full_name, email, password, birth_date }) {
    const body = {
      full_name,
      email,
      password,
      birth_date: birth_date != null && birth_date !== "" ? birth_date : null,
    };
    const res = await fetch(`${BASE}/api/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    return asJson(res);
  },

  async login({ email, password }) {
    const res = await fetch(`${BASE}/api/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
    return asJson(res);
  },

  async me() {
    const res = await fetch(`${BASE}/api/auth/me`, { headers: { ...authHeaders() } });
    return asJson(res);
  },

  async analyze(file, { signal } = {}) {
    const fd = new FormData();
    fd.append("file", file);
    const res = await fetch(`${BASE}/api/analyze`, {
      method: "POST",
      headers: { ...authHeaders() },
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
      headers: { "Content-Type": "application/json", ...authHeaders() },
      body: JSON.stringify(payload),
    });
    return asJson(res);
  },

  async brands() {
    const res = await fetch(`${BASE}/api/brands`);
    return asJson(res);
  },

  async garments({ gender, event, style, feels_like_c } = {}) {
    const params = new URLSearchParams({ gender, event, style });
    if (feels_like_c != null && feels_like_c !== "") {
      params.set("feels_like_c", String(feels_like_c));
    }
    const res = await fetch(`${BASE}/api/garments?${params.toString()}`);
    return asJson(res);
  },

  async tryon({ session_id, garment_id }) {
    const res = await fetch(`${BASE}/api/tryon`, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...authHeaders() },
      body: JSON.stringify({ session_id, garment_id }),
    });
    return asJson(res);
  },

  async sessions() {
    const res = await fetch(`${BASE}/api/sessions`, { headers: { ...authHeaders() } });
    return asJson(res);
  },
};
