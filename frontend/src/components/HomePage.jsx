import React from "react";
import PublicLayout from "./PublicLayout.jsx";

function NavTextButton({ children, onClick }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="text-[11px] uppercase tracking-[0.2em] text-[#a89b8c] hover:text-[#c9a25c] transition px-2.5 py-2 rounded-lg border border-transparent hover:border-white/10"
    >
      {children}
    </button>
  );
}

export default function HomePage({ onEnterStudio, onNavigateAbout, onNavigateHow }) {
  const year = new Date().getFullYear();

  return (
    <PublicLayout
      onHome={() => window.scrollTo({ top: 0, behavior: "smooth" })}
      navRight={
        <>
          <NavTextButton onClick={onNavigateAbout}>About</NavTextButton>
          <NavTextButton onClick={onNavigateHow}>How it works</NavTextButton>
        </>
      }
    >
      <>
        <main className="flex-1 flex flex-col items-center justify-center px-4 py-10 sm:py-14 md:py-16">
          <div className="home-glass-panel w-full max-w-2xl sm:max-w-3xl p-8 sm:p-10 md:p-12 flex flex-col items-center text-center">
            <h1
              className="text-[clamp(2rem,5.5vw,3.75rem)] sm:text-[clamp(2.25rem,6vw,4.25rem)] leading-[1.02] tracking-[-0.02em] text-[#faf6ef] px-1"
              style={{ fontFamily: "'Cormorant Garamond', Georgia, serif" }}
            >
              AI virtual fitting room
            </h1>
            <p
              className="mt-5 sm:mt-6 text-xl sm:text-2xl md:text-[1.75rem] text-[#d4cbbf] font-light tracking-wide max-w-2xl leading-snug"
              style={{ fontFamily: "'Cormorant Garamond', Georgia, serif" }}
            >
              Where your portrait, the weather, and the garment meet — before you ever check out.
            </p>
            <p className="mt-7 sm:mt-8 max-w-xl text-sm sm:text-base text-[#b8aea3] leading-relaxed">
              Upload a portrait for a discreet read on tone and shape, set your city and occasion so we can factor in
              live weather, then browse curated looks and see a virtual try-on in a single, calm studio flow.
            </p>
            <div className="mt-9 sm:mt-10 flex flex-col items-center gap-4">
              <button
                type="button"
                onClick={onEnterStudio}
                className="rounded-xl bg-gradient-to-r from-[#c9a25c] to-[#9a7628] py-3.5 px-12 sm:px-16 text-sm font-semibold text-[#1a120c] shadow-lg shadow-black/40 hover:opacity-95 active:scale-[0.99] transition"
              >
                Enter the studio
              </button>
              <p className="text-[11px] sm:text-xs text-[#7a6f66] tracking-wide">
                Sign in or create an account on the next screen.
              </p>
            </div>
          </div>
        </main>

        <footer className="relative z-20 mt-auto border-t border-white/[0.08] bg-black/35 backdrop-blur-md">
          <div className="max-w-6xl mx-auto px-5 sm:px-10 py-10 sm:py-12">
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-10 sm:gap-8">
              <div>
                <p
                  className="text-lg text-[#f3ede3] mb-2"
                  style={{ fontFamily: "'Cormorant Garamond', Georgia, serif" }}
                >
                  Atelier
                </p>
                <p className="text-xs text-[#8a7d72] leading-relaxed max-w-xs">
                  Virtual try-on with portrait-aware notes, live weather, and a curated catalogue — presented in a
                  quiet, editorial studio experience.
                </p>
              </div>
              <div>
                <p className="text-[10px] uppercase tracking-[0.28em] text-[#c9a25c] mb-4">Company</p>
                <ul className="space-y-2.5 text-sm text-[#c4bbb0]">
                  <li>
                    <button
                      type="button"
                      onClick={onNavigateAbout}
                      className="hover:text-[#f0e6d2] transition border-b border-transparent hover:border-[#c9a25c]/40 text-left"
                    >
                      About us
                    </button>
                  </li>
                  <li>
                    <a
                      href="mailto:hello@atelier.local"
                      className="hover:text-[#f0e6d2] transition border-b border-transparent hover:border-[#c9a25c]/40"
                    >
                      Contact
                    </a>
                  </li>
                  <li>
                    <a
                      href="#privacy"
                      className="hover:text-[#f0e6d2] transition border-b border-transparent hover:border-[#c9a25c]/40"
                    >
                      Privacy
                    </a>
                  </li>
                </ul>
              </div>
              <div>
                <p className="text-[10px] uppercase tracking-[0.28em] text-[#c9a25c] mb-4">Product</p>
                <ul className="space-y-2.5 text-sm text-[#c4bbb0]">
                  <li>
                    <button
                      type="button"
                      onClick={onNavigateHow}
                      className="hover:text-[#f0e6d2] transition border-b border-transparent hover:border-[#c9a25c]/40 text-left"
                    >
                      How it works
                    </button>
                  </li>
                </ul>
              </div>
            </div>
            <p
              id="privacy"
              className="mt-8 text-center text-[11px] text-[#6b615a] max-w-2xl mx-auto leading-relaxed scroll-mt-24"
            >
              <span className="text-[#8a7d72] font-medium uppercase tracking-wider">Privacy · </span>
              [Privacy policy stub — describe how portraits, session data, and third-party AI processing are handled.]
            </p>
            <div className="mt-10 pt-8 border-t border-white/[0.06] flex flex-col sm:flex-row items-center justify-between gap-4 text-[10px] uppercase tracking-[0.2em] text-[#5c534c]">
              <span>© {year} Atelier</span>
              <span className="text-[#5c534c] normal-case tracking-normal text-xs">AI virtual try-on</span>
            </div>
          </div>
        </footer>
      </>
    </PublicLayout>
  );
}
