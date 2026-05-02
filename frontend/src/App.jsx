import React, { useCallback, useEffect, useState } from "react";
import Stepper from "./components/Stepper.jsx";
import UploadStep from "./components/UploadStep.jsx";
import ContextStep from "./components/ContextStep.jsx";
import CatalogStep from "./components/CatalogStep.jsx";
import TryOnStep from "./components/TryOnStep.jsx";
import ResultStep from "./components/ResultStep.jsx";
import { api } from "./api.js";

const STEPS = ["upload", "context", "catalog", "tryon", "result"];

export default function App() {
  const [step, setStep] = useState("upload");
  const [analysis, setAnalysis] = useState(null);
  const [context, setContext] = useState(null);
  const [brands, setBrands] = useState([]);
  const [garment, setGarment] = useState(null);
  const [result, setResult] = useState(null);

  useEffect(() => {
    api.brands().then(setBrands).catch(() => {});
  }, []);

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

  return (
    <div className="min-h-full bg-hero-radial">
      <header className="border-b border-ink-100 bg-white/70 backdrop-blur sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-8 py-4 flex items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="h-9 w-9 rounded-xl bg-gradient-to-br from-accent-500 to-ink-700 grid place-items-center text-white font-bold">
              A
            </div>
            <div>
              <p className="font-display text-xl leading-none">Atelier</p>
              <p className="text-[11px] uppercase tracking-[0.18em] text-ink-400">
                Your virtual fashion studio
              </p>
            </div>
          </div>
          <button className="btn-ghost text-xs" onClick={reset}>
            New session
          </button>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-8 py-8 space-y-8">
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
            onPickAnother={() => setStep("catalog")}
          />
        )}
      </main>

      <footer className="max-w-7xl mx-auto px-4 sm:px-8 py-10 text-center text-xs text-ink-400">
        Crafted with care · Atelier private studio
      </footer>
    </div>
  );
}
