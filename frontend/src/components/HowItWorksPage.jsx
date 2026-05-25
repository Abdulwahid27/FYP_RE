import React from "react";
import PublicLayout from "./PublicLayout.jsx";

const STEPS = [
  {
    n: "01",
    title: "Portrait & analysis",
    body: "Upload a clear portrait. We run a discreet pass for skin tone and face shape notes — shown to you before anything else happens.",
  },
  {
    n: "02",
    title: "Context & weather",
    body: "Choose gender, city, occasion, event, and style. We pull live weather so suggestions stay grounded in how the day actually feels.",
  },
  {
    n: "03",
    title: "Catalogue",
    body: "Browse garments filtered to your selections. Each card links out to the brand when you want full product detail.",
  },
  {
    n: "04",
    title: "Virtual try-on",
    body: "Pick a piece: we prepare a cut-out and run a virtual try-on so you can compare the look before you buy.",
  },
];

export default function HowItWorksPage({ onHome }) {
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
        <div className="w-full max-w-3xl space-y-8">
          <div className="home-glass-panel p-8 sm:p-10 text-left">
            <p className="text-[11px] uppercase tracking-[0.35em] text-[#c9a25c]">How it works</p>
            <h1
              className="mt-2 text-3xl sm:text-4xl text-[#faf6ef] leading-tight"
              style={{ fontFamily: "'Cormorant Garamond', Georgia, serif" }}
            >
              Four steps from welcome to try-on
            </h1>
            <p className="mt-4 text-sm text-[#a89b8c] leading-relaxed">
              Everything runs in the studio after you sign in — one linear flow with a stepper at the top.
            </p>
          </div>
          <ol className="space-y-4">
            {STEPS.map((s) => (
              <li key={s.n} className="home-glass-panel p-6 sm:p-7 flex gap-5">
                <span
                  className="shrink-0 text-2xl sm:text-3xl text-[#c9a25c]/90 font-light w-12 text-center"
                  style={{ fontFamily: "'Cormorant Garamond', Georgia, serif" }}
                >
                  {s.n}
                </span>
                <div>
                  <h2 className="text-lg text-[#f3ede3] font-semibold tracking-tight">{s.title}</h2>
                  <p className="mt-2 text-sm text-[#b8aea3] leading-relaxed">{s.body}</p>
                </div>
              </li>
            ))}
          </ol>
        </div>
      </main>

      <footer className="relative z-20 border-t border-white/[0.08] bg-black/35 backdrop-blur-md py-6 text-center text-[10px] uppercase tracking-[0.22em] text-[#5c534c]">
        © {year} Atelier · AI virtual try-on
      </footer>
      </>
    </PublicLayout>
  );
}
