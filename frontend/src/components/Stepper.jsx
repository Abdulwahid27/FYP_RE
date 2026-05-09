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
                done && "bg-[#1a1510] text-[#f5f0e8] border-[#c9a25c]/40",
                active && "bg-gradient-to-br from-[#c9a25c] to-[#8b6914] text-[#1a120c] border-[#c9a25c] shadow-lg",
                !done && !active && "bg-white/10 text-[#a89b8c] border-white/15",
              ]
                .filter(Boolean)
                .join(" ")}
            >
              {done ? "✓" : i + 1}
            </div>
            <span
              className={[
                "text-sm font-medium",
                active ? "text-[#faf6ef]" : "text-[#a89b8c]",
              ].join(" ")}
            >
              {s.label}
            </span>
            {i < STEPS.length - 1 && (
              <span className="hidden sm:block w-8 h-px bg-white/15" />
            )}
          </li>
        );
      })}
    </ol>
  );
}
