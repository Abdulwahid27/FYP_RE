import React from "react";

/** Shared full-viewport background for auth + logged-in studio (same visual language). */
export default function LuxuryBackdrop() {
  return (
    <>
      <div
        className="pointer-events-none absolute inset-0 opacity-30"
        style={{
          backgroundImage: `
            radial-gradient(ellipse 120% 80% at 10% -10%, rgba(201, 162, 92, 0.35), transparent 55%),
            radial-gradient(ellipse 90% 70% at 100% 20%, rgba(120, 56, 48, 0.45), transparent 50%),
            radial-gradient(ellipse 70% 50% at 50% 100%, rgba(40, 32, 28, 0.9), transparent 55%)
          `,
        }}
      />
      <div
        className="pointer-events-none absolute inset-0 opacity-[0.07] mix-blend-overlay"
        style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.8' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E")`,
        }}
      />
      <div className="pointer-events-none absolute inset-0 bg-gradient-to-b from-black/20 via-transparent to-black/60" />
    </>
  );
}
