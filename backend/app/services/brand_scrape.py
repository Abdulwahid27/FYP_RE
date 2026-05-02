"""
Fetch product-style image URLs from public brand store pages (HTML only).

This does not execute JavaScript. Sites that load products only client-side
may yield few images; adjust CATALOG_SEED_URLS in app/seed.py to a listing
URL that is server-rendered.
"""
from __future__ import annotations

import json
import logging
import re
from html import unescape
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

RE_MEDIA = re.compile(
    r"https?://[^\s\"'<>]+\.(?:jpg|jpeg|png|webp)(?:\?[^\s\"'<>]+)?", re.I
)

# Drop obvious non-product UI assets
EXCLUDE_SUB = (
    "favicon",
    "logo_loader",
    "logo_",
    "/logo",
    "icon_",
    "search-icon",
    "user.png",
    "pak-flag",
    "32x32",
    "add.png",
    "placeholder",
    "makeup",
    "skincare",
    "ruler",
    "payment",
    "sprite",
    "spacer",
    "1x1",
    "menu_tile",
    "Frame_9_",
    "Magento_Theme",
    "currency",
    "GBP",
    "USD",
    "EUR",
    "telephone",
    "email",
    "Category_icon",
    "category_icon",
    "Category-Icon",
    "menu_image",
    "Menu-Images",
    "rtw_menu",
    "capsule_collection_menu",
)

# Extra boost for things that look like product photography
PREFER_SUB = (
    "cdn/shop",
    "demandware",
    "catalog",
    "wysiwyg",
    "_front_",
    "940x",
    "Thumbnails/0.0-",
    "F17",
    "F18",
    "F19",
    "F20",
    "FW-",
    "wp3p",
    "3_piece",
    "2_piece",
    "IPST-",
    "file",
)


def _score(url: str) -> int:
    u = url.lower()
    s = 5
    if any(b in u for b in EXCLUDE_SUB):
        return -100
    for p in PREFER_SUB:
        if p.lower() in u:
            s += 12
    if "width=" in u and ("width=32" in u or "width=146" in u or "width=200" in u):
        s -= 15
    if u.endswith((".png",)) and "cdn/shop" not in u and "lookbook" not in u:
        s -= 5
    if "lookbook" in u or "banner" in u or "hero" in u:
        s -= 3
    return s


def _abs(base: str, u: str) -> str:
    u = u.strip()
    u = u.replace("\\/", "/")
    u = unescape(u)
    if u.startswith("//"):
        u = "https:" + u
    if u.startswith("http://") or u.startswith("https://"):
        return u
    if u.startswith("/"):
        return urljoin(base, u)
    return urljoin(base, u)


def _from_srcset(raw: str, base: str) -> list[str]:
    if not raw:
        return []
    out: list[str] = []
    for part in raw.split(","):
        part = part.strip().split()[0] if part.strip() else ""
        if not part:
            continue
        out.append(_abs(base, part))
    return out


def _json_ld_images(obj, out: list[str]) -> None:
    if obj is None:
        return
    if isinstance(obj, str):
        if obj.startswith("http") and any(obj.lower().endswith(e) for e in (".jpg", ".jpeg", ".png", ".webp")):
            out.append(obj)
        return
    if isinstance(obj, list):
        for it in obj:
            _json_ld_images(it, out)
        return
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k.lower() in ("image", "images", "thumbnail", "url", "contenturl", "logo"):
                _json_ld_images(v, out)
            else:
                _json_ld_images(v, out)


def extract_image_urls_from_html(html: str, final_url: str) -> list[str]:
    out: list[str] = []
    base = f"{urlparse(final_url).scheme}://{urlparse(final_url).netloc}/"

    for script in re.findall(
        r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        html,
        re.I | re.S,
    ):
        try:
            data = json.loads(unescape(script).strip())
        except json.JSONDecodeError:
            continue
        if not isinstance(data, (list, dict)):
            continue
        items = data if isinstance(data, list) else [data]
        for item in items:
            _json_ld_images(item, out)

    soup = BeautifulSoup(html, "lxml")
    for tag in soup.find_all(["img", "source", "a"]):
        for attr in ("src", "data-src", "data-large_image", "href"):
            u = tag.get(attr)
            if u and re.search(r"\.(jpe?g|png|webp)", u, re.I):
                out.append(_abs(str(final_url), u))
        ss = tag.get("srcset")
        if ss:
            out.extend(_from_srcset(ss, str(final_url)))

    for m in RE_MEDIA.finditer(html):
        out.append(m.group(0).rstrip(").,;"))

    # normalize and dedupe by path (ignore width-only query variants for Shopify)
    seen: set[str] = set()
    unique: list[str] = []
    for u in out:
        u = u.strip()
        if not u.startswith("http"):
            continue
        p = urlparse(u)
        key = f"{p.netloc}{p.path}"
        if key in seen:
            continue
        seen.add(key)
        unique.append(u)

    unique.sort(key=_score, reverse=True)
    return [u for u in unique if _score(u) > 0]


def fetch_image_urls_for_brand(
    page_urls: list[str],
    max_images: int = 40,
    timeout: float = 30.0,
) -> list[str]:
    if not page_urls:
        return []
    collected: list[str] = []
    seen_paths: set[str] = set()

    headers = {"User-Agent": USER_AGENT, "Accept": "text/html,application/xhtml+xml"}
    with httpx.Client(
        timeout=timeout,
        follow_redirects=True,
        headers=headers,
    ) as client:
        for page in page_urls:
            try:
                r = client.get(page)
            except httpx.RequestError as e:
                logger.warning("Could not fetch %s: %s", page, e)
                continue
            if r.status_code != 200:
                logger.warning("HTTP %s for %s", r.status_code, page)
                continue
            for u in extract_image_urls_from_html(r.text, str(r.url)):
                p = urlparse(u)
                key = f"{p.netloc}{p.path}"
                if key in seen_paths:
                    continue
                seen_paths.add(key)
                collected.append(u)
                if len(collected) >= max_images:
                    return collected
    collected.sort(key=_score, reverse=True)
    return collected[:max_images]


def fetch_og_image_url(website: str, timeout: float = 20.0) -> str | None:
    """Last-resort: og:image or twitter:image from the brand homepage."""
    if not website or not website.startswith("http"):
        return None
    try:
        with httpx.Client(
            timeout=timeout,
            follow_redirects=True,
            headers={"User-Agent": USER_AGENT, "Accept": "text/html"},
        ) as c:
            r = c.get(website)
    except httpx.RequestError:
        return None
    if r.status_code != 200:
        return None
    soup = BeautifulSoup(r.text, "lxml")
    for tag in soup.find_all("meta"):
        if tag.get("property") in ("og:image", "og:image:secure_url"):
            c = tag.get("content")
            if c and c.startswith("http"):
                return c
        if tag.get("name") in ("twitter:image", "twitter:image:src"):
            c = tag.get("content")
            if c and c.startswith("http"):
                return c
    return None
