import React from "react";

const HERO = "/media/atelier-hero.png";

/**
 * Shared full-bleed hero + header for marketing pages (home, about, how it works).
 * Keeps background layers identical so motion / image are not “disturbed” by page content.
 */
export default function PublicLayout({ children, onHome, navRight }) {
  return (
    <div className="relative min-h-[100dvh] flex flex-col text-[#e8e2d9] overflow-x-hidden bg-[#0c0a09]">
      <div
        className="fixed inset-0 bg-cover bg-center bg-no-repeat scale-105 home-hero-bg pointer-events-none"
        style={{ backgroundImage: `url(${HERO})` }}
        aria-hidden
      />
      <div className="fixed inset-0 bg-gradient-to-b from-[#0c0a09]/88 via-[#0c0a09]/75 to-[#0c0a09]/92 pointer-events-none" aria-hidden />
      <div
        className="fixed inset-0 bg-[radial-gradient(ellipse_120%_80%_at_50%_-20%,rgba(201,162,92,0.12),transparent_55%)] pointer-events-none"
        aria-hidden
      />

      <header className="relative z-20 border-b border-white/[0.08] bg-black/25 backdrop-blur-md">
        <div className="max-w-6xl mx-auto px-5 sm:px-10 py-4 flex items-center justify-between gap-4">
          <button
            type="button"
            onClick={onHome}
            className="flex items-center gap-4 text-left rounded-xl outline-none focus-visible:ring-2 focus-visible:ring-[#c9a25c]/40"
          >
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
          </button>
          {navRight ? <div className="flex items-center gap-2 sm:gap-3 flex-wrap justify-end">{navRight}</div> : null}
        </div>
      </header>

      <div className="relative z-10 flex-1 flex flex-col">{children}</div>
    </div>
  );
}
