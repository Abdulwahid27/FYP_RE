"""Rule-based pick when Gemma vision ranking is unavailable."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..models import Garment, UserSession


def pick_garment_from_catalog_rules(session: "UserSession", garments: list["Garment"]) -> tuple[int | None, str]:
    if not garments:
        return None, ""

    st = (session.skin_tone or "").lower()
    fs = (session.face_shape or "").lower()
    w = session.weather if isinstance(session.weather, dict) else {}
    desc = str(w.get("description") or "").lower()
    try:
        feels_f = float(w["feels_like_c"]) if w.get("feels_like_c") is not None else None
    except (TypeError, ValueError):
        feels_f = None

    best_score = float("-inf")
    best_id = garments[0].id
    for g in garments:
        score = 0.0
        blob = f"{g.title} {g.color or ''} {g.tags or ''} {g.product_type or ''}".lower()

        if any(x in st for x in ("deep", "brown")):
            for kw in ("navy", "emerald", "maroon", "burgundy", "gold", "ivory", "cream", "white", "black"):
                if kw in blob:
                    score += 2.0
        if any(x in st for x in ("fair", "light")):
            for kw in ("pastel", "soft", "powder", "blush", "light", "mint", "lavender"):
                if kw in blob:
                    score += 2.0
        if "medium" in st or "olive" in st or "tan" in st:
            for kw in ("teal", "rust", "camel", "khaki", "navy", "white", "black"):
                if kw in blob:
                    score += 1.5
        if "round" in fs:
            for kw in ("v-neck", "v neck", "collar", "lapel", "structured"):
                if kw in blob:
                    score += 1.0
        if feels_f is not None and feels_f < 18:
            for kw in ("wool", "knit", "warm", "winter"):
                if kw in blob:
                    score += 1.2
        if feels_f is not None and feels_f > 30:
            for kw in ("linen", "cotton", "light", "summer"):
                if kw in blob:
                    score += 1.0
        if "rain" in desc:
            for kw in ("layer", "jacket", "coat"):
                if kw in blob:
                    score += 0.8
        if (g.color or "").strip():
            score += 0.3

        if score > best_score:
            best_score = score
            best_id = g.id

    return (
        best_id,
        "Matched using your skin tone, face shape, occasion, event, style, and today's weather.",
    )
