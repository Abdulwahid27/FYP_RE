import React, { useCallback, useEffect, useState } from "react";
import Stepper from "./components/Stepper.jsx";
import UploadStep from "./components/UploadStep.jsx";
import ContextStep from "./components/ContextStep.jsx";
import CatalogStep from "./components/CatalogStep.jsx";
import TryOnStep from "./components/TryOnStep.jsx";
import ResultStep from "./components/ResultStep.jsx";
import AuthStep from "./components/AuthStep.jsx";
import HomePage from "./components/HomePage.jsx";
import AboutPage from "./components/AboutPage.jsx";
import HowItWorksPage from "./components/HowItWorksPage.jsx";
import LuxuryBackdrop from "./components/LuxuryBackdrop.jsx";
import { api, getToken, setToken as persistToken } from "./api.js";

const STEPS = ["upload", "context", "catalog", "tryon", "result"];

export default function App() {
  const [token, setToken] = useState(() => getToken());
  /** When logged out: show landing first, then auth after "Enter the studio". */
  const [preAuthScreen, setPreAuthScreen] = useState("landing");
  /** Marketing sub-pages while logged out on landing flow (no router dependency). */
  const [publicView, setPublicView] = useState("home");
  const [userLabel, setUserLabel] = useState(null);
  const [step, setStep] = useState("upload");
  const [analysis, setAnalysis] = useState(null);
  const [context, setContext] = useState(null);
  const [brands, setBrands] = useState([]);
  const [garment, setGarment] = useState(null);
  const [result, setResult] = useState(null);

  useEffect(() => {
    api.brands().then(setBrands).catch(() => {});
  }, []);

  // When the API is configured with BOOT_TOKEN_INVALIDATION, /api/health returns a new
  // boot_id per process — clear the JWT so a server restart does not keep the old session.
  useEffect(() => {
    const key = "atelier_api_boot_id";
    const base = import.meta.env.VITE_API_BASE || "";
    fetch(`${base}/api/health`)
      .then((r) => r.json())
      .then((data) => {
        const boot = data?.boot_id;
        if (!boot || typeof boot !== "string") return;
        const prev = localStorage.getItem(key);
        if (prev != null && prev !== boot) {
          persistToken(null);
          setToken(null);
          setPreAuthScreen("landing");
          setPublicView("home");
        }
        localStorage.setItem(key, boot);
      })
      .catch(() => {});
  }, []);

  useEffect(() => {
    if (!token) {
      setUserLabel(null);
      return undefined;
    }
    let cancelled = false;
    api
      .me()
      .then((u) => {
        if (!cancelled) {
          const name = (u.full_name || "").trim();
          setUserLabel(name ? `${name} · ${u.email}` : u.email);
        }
      })
      .catch(() => {
        if (!cancelled) setUserLabel(null);
      });
    return () => {
      cancelled = true;
    };
  }, [token]);

  const onTryonDone = useCallback((r) => {
    setResult(r);
    setStep("result");
  }, []);

  function reset() {
    setStep("upload");
    setAnalysis(null);
    setContext(null);
    setGarment(null);
    setResult(null);
  }

  function logout() {
    persistToken(null);
    setToken(null);
    setPreAuthScreen("landing");
    setPublicView("home");
    reset();
  }

  if (!token) {
    if (preAuthScreen === "landing") {
      if (publicView === "about") {
        return <AboutPage onHome={() => setPublicView("home")} />;
      }
      if (publicView === "how") {
        return <HowItWorksPage onHome={() => setPublicView("home")} />;
      }
      return (
        <HomePage
          onEnterStudio={() => setPreAuthScreen("auth")}
          onNavigateAbout={() => setPublicView("about")}
          onNavigateHow={() => setPublicView("how")}
        />
      );
    }
    return (
      <AuthStep
        onBackHome={() => {
          setPreAuthScreen("landing");
          setPublicView("home");
        }}
        onAuthed={(t) => {
          persistToken(t);
          setToken(t);
        }}
      />
    );
  }

  return (
    <div className="luxury-app relative min-h-full flex flex-col overflow-hidden bg-[#0c0a09] text-[#e8e2d9]">
      <LuxuryBackdrop />

      <header className="relative z-10 border-b border-white/[0.08] bg-black/25 backdrop-blur-md sticky top-0">
        <div className="max-w-7xl mx-auto px-4 sm:px-8 py-4 flex items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-2xl bg-gradient-to-br from-[#c9a25c] via-[#8b6914] to-[#3d2a12] ring-1 ring-white/10 grid place-items-center text-xs font-semibold text-[#1a1510]">
              A
            </div>
            <div>
              <p
                className="text-xl leading-none text-[#f3ede3]"
                style={{ fontFamily: "'Cormorant Garamond', Georgia, serif" }}
              >
                Atelier
              </p>
              <p className="text-[10px] uppercase tracking-[0.28em] text-[#a89b8c] mt-0.5">AI virtual try-on</p>
            </div>
          </div>
          <div className="flex items-center gap-3 flex-wrap justify-end">
            {userLabel && (
              <span className="text-xs text-[#a89b8c] max-w-[240px] truncate" title={userLabel}>
                {userLabel}
              </span>
            )}
            <button className="btn-ghost text-xs" onClick={reset}>
              New session
            </button>
            <button className="btn-ghost text-xs text-[#c9bfb2]" onClick={logout}>
              Log out
            </button>
          </div>
        </div>
      </header>

      <main className="relative z-10 flex-1 max-w-7xl w-full mx-auto px-4 sm:px-8 py-8 space-y-8">
        <div className="card px-6 py-4">
          <Stepper current={step} />
        </div>

        {step === "upload" && (
          <UploadStep
            onAnalyzed={(a) => {
              setAnalysis(a);
              setStep("context");
            }}
          />
        )}

        {step === "context" && analysis && (
          <ContextStep
            analysis={analysis}
            onBack={() => setStep("upload")}
            onContinue={(ctx) => {
              setContext(ctx);
              setStep("catalog");
            }}
          />
        )}

        {step === "catalog" && analysis && context && (
          <CatalogStep
            analysis={analysis}
            context={context}
            brands={brands}
            onBack={() => setStep("context")}
            onPick={(g) => {
              setGarment(g);
              setStep("tryon");
            }}
          />
        )}

        {step === "tryon" && analysis && garment && (
          <TryOnStep
            analysis={analysis}
            garment={garment}
            onBack={() => setStep("catalog")}
            onDone={onTryonDone}
          />
        )}

        {step === "result" && result && garment && (
          <ResultStep
            result={result}
            garment={garment}
            onRestart={reset}
            onPickAnother={() => {
              setResult(null);
              setGarment(null);
              setStep("catalog");
            }}
          />
        )}
      </main>

      <footer className="relative z-10 border-t border-white/[0.06] py-8 text-center text-[10px] uppercase tracking-[0.22em] text-[#5c534c]">
        Atelier · AI virtual try-on
      </footer>
    </div>
  );
}
