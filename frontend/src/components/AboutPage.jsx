import React from "react";
import PublicLayout from "./PublicLayout.jsx";

export default function AboutPage({ onHome }) {
  const year = new Date().getFullYear();

  return (
    <PublicLayout
      onHome={onHome}
      navRight={
        <button
          type="button"
          onClick={onHome}
          className="text-[11px] uppercase tracking-[0.2em] text-[#a89b8c] hover:text-[#c9a25c] transition px-3 py-2 rounded-lg border border-white/10 hover:border-white/15"
        >
          ← Home
        </button>
      }
    >
      <>
      <main className="flex-1 flex flex-col items-center px-4 py-12 sm:py-16">
        <article className="home-glass-panel w-full max-w-3xl p-8 sm:p-10 md:p-12 space-y-6 text-left">
          <p className="text-[11px] uppercase tracking-[0.35em] text-[#c9a25c]">About us</p>
          <h1
            className="text-3xl sm:text-4xl text-[#faf6ef] leading-tight"
            style={{ fontFamily: "'Cormorant Garamond', Georgia, serif" }}
          >
            A calm studio for virtual try-on
          </h1>
          <div className="space-y-4 text-sm sm:text-base text-[#c4bbb0] leading-relaxed">
            <p>
              Atelier brings together portrait-aware styling notes, real weather for your city, and a curated catalogue
              so you can preview how garments might read on you — before you commit to a purchase.
            </p>
            <p>
              We keep the interface quiet and editorial: gold accents on deep ink tones, clear steps from upload to
              try-on, and no noisy claims about “replacing” a fitting room — only a thoughtful digital mirror.
            </p>
            <p className="text-[#8a7d72] text-sm">
              Images you upload are used for analysis and virtual try-on within your session. Use the product only
              where you are comfortable sharing a portrait with the configured AI services.
            </p>
          </div>
        </article>
      </main>

      <footer className="relative z-20 border-t border-white/[0.08] bg-black/35 backdrop-blur-md py-6 text-center text-[10px] uppercase tracking-[0.22em] text-[#5c534c]">
        © {year} Atelier · AI virtual try-on
      </footer>
      </>
    </PublicLayout>
  );
}
