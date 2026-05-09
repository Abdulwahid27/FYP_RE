"""Fetch real product data from Shopify storefront JSON endpoints."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

import httpx


USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)


@dataclass
class ShopifyProduct:
    title: str
    image_url: str
    product_url: str
    price: Optional[str]
    color: Optional[str]
    product_type: Optional[str] = None
    tags: Optional[str] = None


def _format_price(variants: list[dict]) -> Optional[str]:
    if not variants:
        return None
    raw = variants[0].get("price")
    if raw in (None, "", "0", "0.00"):
        return None
    try:
        amount = float(raw)
    except (TypeError, ValueError):
        return None
    return f"PKR {amount:,.0f}"


def _pick_image(product: dict[str, Any]) -> Optional[str]:
    images = product.get("images") or []
    for img in images:
        src = img.get("src")
        if src:
            return str(src)
    return None


_SIZE_TOKENS = {
    "xxs", "xs", "s", "m", "l", "xl", "xxl", "xxxl",
    "small", "medium", "large",
    "free size", "one size", "os", "n/a",
}


def _guess_color(product: dict[str, Any]) -> Optional[str]:
    options = product.get("options") or []
    color_pos: Optional[int] = None
    for o in options:
        name = (o.get("name") or "").strip().lower()
        if name in {"color", "colour", "shade"}:
            pos = o.get("position")
            if isinstance(pos, int):
                color_pos = pos
                break

    variants = product.get("variants") or []
    if color_pos and variants:
        v = variants[0]
        val = v.get(f"option{color_pos}")
        if isinstance(val, str):
            t = val.strip()
            if t:
                return t

    for v in variants:
        for key in ("option2", "option3", "option1"):
            val = v.get(key)
            if not isinstance(val, str):
                continue
            t = val.strip()
            if not t:
                continue
            if t.lower() in _SIZE_TOKENS:
                continue
            if any(c.isdigit() for c in t):
                continue
            if len(t) > 30:
                continue
            return t
    return None


def _tags_blob(product: dict[str, Any]) -> Optional[str]:
    raw = product.get("tags")
    if isinstance(raw, list):
        return " ".join(str(t) for t in raw)
    if isinstance(raw, str):
        return raw
    return None


def dict_to_shopify_product(base_url: str, product: dict[str, Any]) -> Optional[ShopifyProduct]:
    image_url = _pick_image(product)
    handle_p = product.get("handle")
    if not image_url or not handle_p:
        return None
    pt_raw = product.get("product_type")
    product_type = str(pt_raw).strip()[:120] if pt_raw else None

    return ShopifyProduct(
        title=(product.get("title") or "").strip()[:200] or "Untitled",
        image_url=image_url,
        product_url=f"{base_url.rstrip('/')}/products/{handle_p}",
        price=_format_price(product.get("variants") or []),
        color=_guess_color(product),
        product_type=product_type,
        tags=_tags_blob(product),
    )


def fetch_collection_raw_products(
    base_url: str,
    handle: str,
    *,
    limit: int = 50,
    timeout: float = 25.0,
) -> list[dict[str, Any]]:
    url = f"{base_url.rstrip('/')}/collections/{handle}/products.json?limit={limit}"
    headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    try:
        with httpx.Client(timeout=timeout, follow_redirects=True) as client:
            r = client.get(url, headers=headers)
            r.raise_for_status()
            data = r.json()
    except (httpx.HTTPError, ValueError):
        return []
    return list(data.get("products") or [])[:limit]


def fetch_collection_products(
    base_url: str,
    handle: str,
    *,
    limit: int = 12,
    timeout: float = 20.0,
) -> list[ShopifyProduct]:
    """Back-compat helper: raw → ``ShopifyProduct`` (no catalogue heuristics)."""
    out: list[ShopifyProduct] = []
    for p in fetch_collection_raw_products(base_url, handle, limit=limit, timeout=timeout):
        sp = dict_to_shopify_product(base_url, p)
        if sp:
            out.append(sp)
        if len(out) >= limit:
            break
    return out
