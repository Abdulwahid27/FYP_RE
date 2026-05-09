"""Heuristic filters for catalogue rows (upper-body only + weather-aware display).

Shopify collections often mix tops with trousers, bags, and seasonal knitwear.
We keep *all* qualifying rows in the database so cold-weather sessions can still
surface jackets — then ``GET /api/garments`` optionally filters by
``feels_like_c`` from the user's OpenWeather snapshot.
"""
from __future__ import annotations

import re
from typing import Any

# Bottom / legwear / bags / socks — never shown as a try-on garment.
_BOTTOM_TITLE = re.compile(
    r"\b("
    r"jeans?|joggers?|trousers?|chinos?|pants?|palazzos?|"
    r"cargo\s*pants?|wide\s*leg\s*pants?|leggings?|tights?|"
    r"skorts?|shorts?\b|half\s*pants?|"
    r"shalwar\s*only|trouser\s*only|"
    r"\bsocks?\b|\bbag\b|hand\s*bag|tote|clutch|"
    r"footwear|sneakers?|shoes?\b|sandals?\b|chappal|khussa"
    r")\b",
    re.I,
)

_BOTTOM_TYPES = {
    "JEANS",
    "JOGGERS",
    "TROUSER",
    "TROUSERS",
    "Trouser",
    "PANTS",
    "SHORTS",
    "SKIRT",
    "LEGGINGS",
    "SWEATPANTS",
    "SOCKS",
    "BAGS",
    "SHOES",
    "FOOTWEAR",
    "SNEAKERS",
    "SANDALS",
}

_EXCLUDE_TYPES_SUBSTRING = (
    "trouser",
    "jean",
    "bottom",
    "sock",
    "footwear",
    "shoe",
    "sandal",
    "bag",
)

# When it feels hot (°C), hide obvious cold-weather / knit layers from the grid.
_HOT_WEATHER_EXCLUDE = re.compile(
    r"\b("
    r"winter|fleece|puffer|quilted|thermal|sweatshirt|hoodie|"
    r"cardigan|sweater|jacket|coat|down\s*fill|fur\b|"
    r"velvet|wool\s*tweed|tweed\s*vest|mockneck\s*sweater|"
    r"turtle\s*neck\s*sweater|half\s*zip\s*sweater|zipdown\s*sweater|"
    r"knitwear|padded|insulated|ski\b"
    r")\b",
    re.I,
)

_HEAVY_WINTER_ONLY = re.compile(
    r"\b(puffer|fleece|thermal|quilted|down\s*fill|ski\b)\b",
    re.I,
)


def _norm_type(product_type: str | None) -> str:
    return (product_type or "").strip().lower()


def is_upper_body_shopify_product(product: dict[str, Any]) -> bool:
    """Return False for bottoms, bags, socks, footwear, etc."""
    title = (product.get("title") or "").strip()
    ptype = _norm_type(product.get("product_type"))

    # Co-ord eastern titles often say "KURTA TROUSERS" / "KAMEEZ SHALWAR" — keep those.
    if re.search(
        r"\b(kurta.*trouser|trouser.*kurta|kameez.*shalwar|shalwar.*kameez|"
        r"kurta.*pajama|pajama.*kurta)\b",
        title,
        re.I,
    ):
        pass
    elif _BOTTOM_TITLE.search(title):
        return False

    pt_up = (product.get("product_type") or "").strip().upper()
    if pt_up in _BOTTOM_TYPES:
        return False

    for frag in _EXCLUDE_TYPES_SUBSTRING:
        if frag in ptype:
            return False

    return True


def passes_feels_like_filter(
    *,
    title: str | None,
    product_type: str | None,
    tags: str | None,
    feels_like_c: float | None,
) -> bool:
    """Filter garments for the *current* weather context.

    - ``feels_like_c is None`` → no weather filter (show everything in bucket).
    - ``feels_like_c >= 22`` → Pakistan summer / hot: hide winter knitwear.
    - ``feels_like_c <= 17`` → cool: show everything (including jackets).
    - Between → hide only the heaviest winter keywords.
    """
    if feels_like_c is None:
        return True

    blob = " ".join(
        [
            (title or ""),
            (product_type or ""),
            (tags or ""),
        ]
    )

    if feels_like_c >= 22.0:
        return not _HOT_WEATHER_EXCLUDE.search(blob)

    if feels_like_c <= 17.0:
        return True

    return not _HEAVY_WINTER_ONLY.search(blob)


