import React from "react";

const STEPS = [
  { key: "upload", label: "Portrait" },
  { key: "context", label: "Context" },
  { key: "catalog", label: "Catalog" },
  { key: "tryon", label: "Try-On" },
  { key: "result", label: "Result" },
];

export default function Stepper({ current }) {
  const currentIdx = STEPS.findIndex((s) => s.key === current);
  return (
    <ol className="flex items-center gap-2 sm:gap-4 overflow-x-auto">
      {STEPS.map((s, i) => {
        const done = i < currentIdx;
        const active = i === currentIdx;
        return (
          <li key={s.key} className="flex items-center gap-2 sm:gap-3 shrink-0">
            <div
              className={[
                "h-8 w-8 rounded-full flex items-center justify-center text-xs font-bold border transition",
                done && "bg-ink-900 text-white border-ink-900",
                active && "bg-accent-500 text-white border-accent-500 shadow-glow",
                !done && !active && "bg-white text-ink-400 border-ink-200",
              ]
                .filter(Boolean)
                .join(" ")}
            >
              {done ? "✓" : i + 1}
            </div>
            <span
              className={[
                "text-sm font-medium",
                active ? "text-ink-900" : "text-ink-500",
              ].join(" ")}
            >
              {s.label}
            </span>
            {i < STEPS.length - 1 && (
              <span className="hidden sm:block w-8 h-px bg-ink-200" />
            )}
          </li>
        );
      })}
    </ol>
  );
}
