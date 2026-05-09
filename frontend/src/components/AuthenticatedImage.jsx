import React, { useEffect, useState } from "react";
import { authHeaders } from "../api.js";

function absoluteFetchUrl(path) {
  if (!path) return "";
  if (path.startsWith("http")) return path;
  const base = import.meta.env.VITE_API_BASE || "";
  return `${base}${path}`;
}

export default function AuthenticatedImage({ src, alt, className }) {
  const [blobUrl, setBlobUrl] = useState(null);
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    if (!src) return undefined;
    let cancelled = false;
    let objectUrl;
    (async () => {
      try {
        const res = await fetch(absoluteFetchUrl(src), { headers: { ...authHeaders() } });
        if (!res.ok) throw new Error("unauthorized or missing");
        const blob = await res.blob();
        if (cancelled) return;
        objectUrl = URL.createObjectURL(blob);
        setBlobUrl(objectUrl);
        setFailed(false);
      } catch {
        if (!cancelled) {
          setFailed(true);
          setBlobUrl(null);
        }
      }
    })();
    return () => {
      cancelled = true;
      if (objectUrl) URL.revokeObjectURL(objectUrl);
    };
  }, [src]);

  if (!src) return null;
  if (failed) {
    return (
      <div className={`${className || ""} grid place-items-center bg-ink-100 text-ink-400 text-xs p-4`}>
        Sign in again or reload if the image does not appear.
      </div>
    );
  }
  if (!blobUrl) {
    return <div className={`${className || ""} bg-ink-100 animate-pulse min-h-[120px]`} aria-hidden />;
  }
  return <img src={blobUrl} alt={alt || ""} className={className} />;
}
