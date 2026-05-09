import React, { useState } from "react";
import { api } from "../api.js";
import LuxuryBackdrop from "./LuxuryBackdrop.jsx";

export default function AuthStep({ onAuthed, onBackHome }) {
  const [mode, setMode] = useState("login");
  const [registerDone, setRegisterDone] = useState(null);

  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [birthDate, setBirthDate] = useState("");
  const [password, setPassword] = useState("");
  const [password2, setPassword2] = useState("");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  function switchMode(next) {
    setMode(next);
    setError(null);
    if (next === "login") {
      setPassword2("");
    }
  }

  async function handleLogin(e) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const { access_token } = await api.login({ email: email.trim(), password });
      onAuthed(access_token);
    } catch (err) {
      setError(err.message || "Could not sign in.");
    } finally {
      setLoading(false);
    }
  }

  async function handleRegister(e) {
    e.preventDefault();
    setError(null);
    if (password !== password2) {
      setError("Passwords do not match.");
      return;
    }
    setLoading(true);
    try {
      const res = await api.register({
        full_name: fullName.trim(),
        email: email.trim(),
        password,
        birth_date: birthDate.trim() || null,
      });
      setRegisterDone(res);
      setPassword("");
      setPassword2("");
      setMode("login");
    } catch (err) {
      setError(err.message || "Registration failed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-full relative flex flex-col overflow-hidden bg-[#0c0a09] text-[#e8e2d9]">
      <LuxuryBackdrop />

      <header className="relative z-10 border-b border-white/[0.08] bg-black/20 backdrop-blur-md">
        <div className="max-w-6xl mx-auto px-5 sm:px-10 py-5 flex items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="h-11 w-11 rounded-2xl bg-gradient-to-br from-[#c9a25c] via-[#8b6914] to-[#3d2a12] shadow-lg ring-1 ring-white/10 grid place-items-center text-sm font-semibold tracking-tight text-[#1a1510]">
              A
            </div>
            <div>
              <p
                className="text-2xl sm:text-[1.65rem] tracking-[0.02em] text-[#f3ede3]"
                style={{ fontFamily: "'Cormorant Garamond', Georgia, serif" }}
              >
                Atelier
              </p>
              <p className="text-[10px] uppercase tracking-[0.35em] text-[#a89b8c] mt-0.5">AI virtual try-on</p>
            </div>
          </div>
          <div className="flex items-center gap-3 justify-end">
            {typeof onBackHome === "function" && (
              <button
                type="button"
                onClick={onBackHome}
                className="text-[11px] uppercase tracking-[0.2em] text-[#a89b8c] hover:text-[#c9a25c] transition px-2 py-1 rounded-lg border border-transparent hover:border-white/10"
              >
                ← Home
              </button>
            )}
            <p className="hidden sm:block text-xs text-[#8a7d72] max-w-xs text-right leading-relaxed">
              Sign in to upload your portrait, get style notes, and try looks virtually.
            </p>
          </div>
        </div>
      </header>

      <main className="relative z-10 flex-1 flex items-stretch justify-center px-4 py-10 sm:py-14">
        <div className="w-full max-w-5xl grid lg:grid-cols-[1fr_1.05fr] gap-8 lg:gap-12 items-center">
          <section className="hidden lg:flex flex-col justify-center space-y-6 pr-4">
            <p className="text-[11px] uppercase tracking-[0.4em] text-[#c9a25c]">Welcome</p>
            <h1
              className="text-4xl xl:text-[2.75rem] leading-[1.12] text-[#faf6ef]"
              style={{ fontFamily: "'Cormorant Garamond', Georgia, serif" }}
            >
              Your look, fitted in the mirror before you buy.
            </h1>
            <p className="text-sm text-[#a89b8c] leading-relaxed max-w-md">
              Atelier uses AI to read your portrait, suggest directions, and show a virtual try-on so you
              can decide with confidence.
            </p>
          </section>

          <section className="w-full max-w-md mx-auto lg:max-w-none">
            <div className="rounded-[1.75rem] border border-white/[0.12] bg-[#141110]/85 backdrop-blur-xl shadow-[0_25px_80px_-20px_rgba(0,0,0,0.85)] overflow-hidden">
              <div className="grid grid-cols-2 border-b border-white/[0.08]">
                <button
                  type="button"
                  onClick={() => switchMode("login")}
                  className={`py-4 text-sm font-semibold tracking-wide transition ${
                    mode === "login"
                      ? "bg-[#c9a25c]/15 text-[#f3ede3] border-b-2 border-[#c9a25c]"
                      : "text-[#7a6f66] hover:text-[#c4bbb0]"
                  }`}
                >
                  Sign in
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setRegisterDone(null);
                    switchMode("register");
                  }}
                  className={`py-4 text-sm font-semibold tracking-wide transition ${
                    mode === "register"
                      ? "bg-[#c9a25c]/15 text-[#f3ede3] border-b-2 border-[#c9a25c]"
                      : "text-[#7a6f66] hover:text-[#c4bbb0]"
                  }`}
                >
                  Sign up
                </button>
              </div>

              <div className="p-7 sm:p-9 space-y-6">
                {registerDone && mode === "login" && (
                  <div
                    role="status"
                    className="rounded-2xl border border-[#c9a25c]/35 bg-[#c9a25c]/10 px-4 py-3 text-sm text-[#ebe4d9] leading-relaxed"
                  >
                    <p className="font-semibold text-[#f0e6d2]">You&apos;re registered.</p>
                    <p className="mt-1 text-[#c9bfb2]">{registerDone.message}</p>
                    <p className="mt-2 text-xs text-[#a89b8c]">
                      Signing in as <span className="text-[#e8dcc8]">{registerDone.email}</span>
                    </p>
                  </div>
                )}

                {mode === "login" ? (
                  <form onSubmit={handleLogin} className="space-y-5">
                    <div>
                      <h2
                        className="text-xl text-[#f5f0e8]"
                        style={{ fontFamily: "'Cormorant Garamond', Georgia, serif" }}
                      >
                        Welcome back
                      </h2>
                      <p className="text-xs text-[#8a7d72] mt-1">Use the email and password you chose at registration.</p>
                    </div>
                    <div>
                      <label className="block text-[10px] uppercase tracking-[0.2em] text-[#a89b8c] mb-2" htmlFor="login-email">
                        Email
                      </label>
                      <input
                        id="login-email"
                        type="email"
                        autoComplete="email"
                        required
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        className="w-full rounded-xl border border-white/10 bg-black/30 px-4 py-3 text-sm text-[#f3ede3] placeholder:text-[#5c534c] focus:border-[#c9a25c]/50 focus:outline-none focus:ring-1 focus:ring-[#c9a25c]/30"
                        placeholder="you@example.com"
                      />
                    </div>
                    <div>
                      <label className="block text-[10px] uppercase tracking-[0.2em] text-[#a89b8c] mb-2" htmlFor="login-password">
                        Password
                      </label>
                      <input
                        id="login-password"
                        type="password"
                        autoComplete="current-password"
                        required
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        className="w-full rounded-xl border border-white/10 bg-black/30 px-4 py-3 text-sm text-[#f3ede3] focus:border-[#c9a25c]/50 focus:outline-none focus:ring-1 focus:ring-[#c9a25c]/30"
                        placeholder="••••••••"
                      />
                    </div>
                    {error && (
                      <p className="text-sm text-[#f0b4a8] bg-[#3a1f1a]/50 border border-[#5c2e28]/50 rounded-xl px-4 py-2">{error}</p>
                    )}
                    <button
                      type="submit"
                      disabled={loading}
                      className="w-full rounded-xl bg-gradient-to-r from-[#c9a25c] to-[#9a7628] py-3.5 text-sm font-semibold text-[#1a120c] shadow-lg hover:opacity-95 active:scale-[0.99] transition disabled:opacity-50"
                    >
                      {loading ? "Entering…" : "Enter the studio"}
                    </button>
                  </form>
                ) : (
                  <form onSubmit={handleRegister} className="space-y-5">
                    <div>
                      <h2
                        className="text-xl text-[#f5f0e8]"
                        style={{ fontFamily: "'Cormorant Garamond', Georgia, serif" }}
                      >
                        Create your account
                      </h2>
                      <p className="text-xs text-[#8a7d72] mt-1">
                        Full name is required. Date of birth is optional — we use it only to refine age-aware suggestions.
                      </p>
                    </div>
                    <div>
                      <label className="block text-[10px] uppercase tracking-[0.2em] text-[#a89b8c] mb-2" htmlFor="reg-name">
                        Full name
                      </label>
                      <input
                        id="reg-name"
                        type="text"
                        autoComplete="name"
                        required
                        minLength={2}
                        value={fullName}
                        onChange={(e) => setFullName(e.target.value)}
                        className="w-full rounded-xl border border-white/10 bg-black/30 px-4 py-3 text-sm text-[#f3ede3] placeholder:text-[#5c534c] focus:border-[#c9a25c]/50 focus:outline-none focus:ring-1 focus:ring-[#c9a25c]/30"
                        placeholder="As you'd like it to appear"
                      />
                    </div>
                    <div>
                      <label className="block text-[10px] uppercase tracking-[0.2em] text-[#a89b8c] mb-2" htmlFor="reg-email">
                        Email
                      </label>
                      <input
                        id="reg-email"
                        type="email"
                        autoComplete="email"
                        required
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        className="w-full rounded-xl border border-white/10 bg-black/30 px-4 py-3 text-sm text-[#f3ede3] placeholder:text-[#5c534c] focus:border-[#c9a25c]/50 focus:outline-none focus:ring-1 focus:ring-[#c9a25c]/30"
                        placeholder="you@example.com"
                      />
                    </div>
                    <div>
                      <label className="block text-[10px] uppercase tracking-[0.2em] text-[#a89b8c] mb-2" htmlFor="reg-dob">
                        Date of birth <span className="lowercase tracking-normal text-[#6b615a]">(optional)</span>
                      </label>
                      <input
                        id="reg-dob"
                        type="date"
                        value={birthDate}
                        max={new Date().toISOString().slice(0, 10)}
                        onChange={(e) => setBirthDate(e.target.value)}
                        className="w-full rounded-xl border border-white/10 bg-black/30 px-4 py-3 text-sm text-[#f3ede3] focus:border-[#c9a25c]/50 focus:outline-none focus:ring-1 focus:ring-[#c9a25c]/30 [color-scheme:dark]"
                      />
                    </div>
                    <div>
                      <label className="block text-[10px] uppercase tracking-[0.2em] text-[#a89b8c] mb-2" htmlFor="reg-password">
                        Password
                      </label>
                      <input
                        id="reg-password"
                        type="password"
                        autoComplete="new-password"
                        required
                        minLength={8}
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        className="w-full rounded-xl border border-white/10 bg-black/30 px-4 py-3 text-sm text-[#f3ede3] focus:border-[#c9a25c]/50 focus:outline-none focus:ring-1 focus:ring-[#c9a25c]/30"
                        placeholder="At least 8 characters"
                      />
                    </div>
                    <div>
                      <label className="block text-[10px] uppercase tracking-[0.2em] text-[#a89b8c] mb-2" htmlFor="reg-password2">
                        Confirm password
                      </label>
                      <input
                        id="reg-password2"
                        type="password"
                        autoComplete="new-password"
                        required
                        minLength={8}
                        value={password2}
                        onChange={(e) => setPassword2(e.target.value)}
                        className="w-full rounded-xl border border-white/10 bg-black/30 px-4 py-3 text-sm text-[#f3ede3] focus:border-[#c9a25c]/50 focus:outline-none focus:ring-1 focus:ring-[#c9a25c]/30"
                        placeholder="Repeat password"
                      />
                    </div>
                    {error && (
                      <p className="text-sm text-[#f0b4a8] bg-[#3a1f1a]/50 border border-[#5c2e28]/50 rounded-xl px-4 py-2">{error}</p>
                    )}
                    <button
                      type="submit"
                      disabled={loading}
                      className="w-full rounded-xl border border-[#c9a25c]/40 bg-[#c9a25c]/10 py-3.5 text-sm font-semibold text-[#f0e6d2] hover:bg-[#c9a25c]/20 transition disabled:opacity-50"
                    >
                      {loading ? "Submitting…" : "Create account"}
                    </button>
                    <p className="text-[11px] text-[#6b615a] leading-relaxed">
                      After you submit, you&apos;ll see a confirmation here — then sign in on the Sign in tab.
                    </p>
                  </form>
                )}
              </div>
            </div>
          </section>
        </div>
      </main>

      <footer className="relative z-10 border-t border-white/[0.06] py-6 text-center text-[10px] uppercase tracking-[0.25em] text-[#5c534c]">
        Atelier · AI virtual try-on
      </footer>
    </div>
  );
}
