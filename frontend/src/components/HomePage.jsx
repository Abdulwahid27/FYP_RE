import React from "react";

const HERO = "/media/atelier-hero.png";

export default function HomePage({ onEnterStudio }) {
  return (
    <div className="relative min-h-[100dvh] min-h-full flex flex-col text-[#e8e2d9] overflow-hidden bg-[#0c0a09]">
      {/* Full-bleed hero */}
      <div
        className="absolute inset-0 bg-cover bg-center bg-no-repeat scale-105 home-hero-bg"
        style={{ backgroundImage: `url(${HERO})` }}
        aria-hidden
      />
      <div className="absolute inset-0 bg-gradient-to-b from-[#0c0a09]/88 via-[#0c0a09]/75 to-[#0c0a09]/92" aria-hidden />
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_120%_80%_at_50%_-20%,rgba(201,162,92,0.12),transparent_55%)]" aria-hidden />

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
        </div>
      </header>

      <main className="relative z-10 flex-1 flex flex-col items-center justify-center px-4 py-12 sm:py-16">
        <div className="home-glass-panel w-full max-w-lg sm:max-w-xl p-8 sm:p-10 md:p-12 text-center space-y-6 sm:space-y-8">
          <p className="text-[11px] uppercase tracking-[0.4em] text-[#c9a25c]">Virtual fitting room</p>
          <h1
            className="text-3xl sm:text-4xl md:text-[2.65rem] leading-[1.12] text-[#faf6ef] px-1"
            style={{ fontFamily: "'Cormorant Garamond', Georgia, serif" }}
          >
            See the garment on you before it ships.
          </h1>
          <p className="text-sm sm:text-base text-[#c4bbb0] leading-relaxed max-w-md mx-auto">
            Upload a portrait, get a gentle read on tone and shape, then try curated looks in a private studio
            session — same gold-and-ink aesthetic, now with a clearer welcome.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-3 sm:gap-4 pt-2">
            <button
              type="button"
              onClick={onEnterStudio}
              className="w-full sm:w-auto min-w-[200px] rounded-xl bg-gradient-to-r from-[#c9a25c] to-[#9a7628] py-3.5 px-8 text-sm font-semibold text-[#1a120c] shadow-lg shadow-black/40 hover:opacity-95 active:scale-[0.99] transition"
            >
              Enter the studio
            </button>
            <p className="text-[11px] text-[#7a6f66] max-w-[220px] sm:text-left">
              Sign in or create an account on the next screen.
            </p>
          </div>
        </div>
      </main>

      <footer className="relative z-10 border-t border-white/[0.06] py-6 text-center text-[10px] uppercase tracking-[0.25em] text-[#5c534c] bg-black/15 backdrop-blur-sm">
        Atelier · AI virtual try-on
      </footer>
    </div>
  );
}
