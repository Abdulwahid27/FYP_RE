import asyncio
import base64
import json
import logging
import re
from pathlib import Path
from typing import Any, TYPE_CHECKING

import httpx

if TYPE_CHECKING:
    from ..models import Garment, UserSession

from ..config import settings


logger = logging.getLogger(__name__)


SYSTEM_PROMPT = (
    "You are a careful visual analyst. Look at the provided portrait photo and return ONLY a "
    "compact JSON object describing the person's apparent skin tone and face shape. "
    "Use these vocabularies: "
    "skin_tone: one of [fair, light, medium, olive, tan, brown, deep]. "
    "face_shape: one of [oval, round, square, heart, diamond, oblong, triangle]. "
    "Return strictly valid JSON with keys skin_tone and face_shape. No prose, no markdown."
)

USER_PROMPT = (
    "Analyze this portrait and respond with JSON only: "
    '{"skin_tone": "...", "face_shape": "..."}'
)

# Single in-flight request guard — never hit the upstream more than once at a time.
_request_lock = asyncio.Lock()
_recommend_lock = asyncio.Lock()

# Backoff (seconds) after HTTP 429. We deliberately allow ONE retry only —
# every retry burns another upstream call on a shared free quota, so we'd rather
# fail fast and let the user choose to retry manually.
RETRY_BACKOFF_SECONDS: list[float] = [8.0]


class StyleAnalysisError(Exception):
    """User-friendly error raised when the upstream model can't be reached."""


def _encode_image_to_data_url(image_path: Path) -> str:
    suffix = image_path.suffix.lower().lstrip(".")
    mime = "jpeg" if suffix in ("jpg", "jpeg") else suffix or "png"
    b = image_path.read_bytes()
    return f"data:image/{mime};base64,{base64.b64encode(b).decode('utf-8')}"


def _subtype_from_content_type(content_type: str) -> str:
    ct = (content_type or "").split(";")[0].strip().lower()
    if ct in ("image/jpeg", "image/jpg"):
        return "jpeg"
    if ct == "image/png":
        return "png"
    if ct == "image/webp":
        return "webp"
    return "png"


def _encode_bytes_to_data_url(content_type: str, raw: bytes) -> str:
    sub = _subtype_from_content_type(content_type)
    return f"data:image/{sub};base64,{base64.b64encode(raw).decode('utf-8')}"


def _portrait_to_data_url(image: Path | tuple[str, bytes]) -> str:
    if isinstance(image, Path):
        return _encode_image_to_data_url(image)
    mime, raw = image
    return _encode_bytes_to_data_url(mime, raw)


def _extract_json(text: str) -> dict[str, Any] | None:
    if not text:
        return None
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.S)
    candidate = fenced.group(1) if fenced else None
    if not candidate:
        m = re.search(r"\{[^{}]*\}", text, re.S)
        candidate = m.group(0) if m else None
    if not candidate:
        return None
    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        return None


def _openrouter_error_body(resp: httpx.Response) -> str:
    try:
        data = resp.json()
        err = data.get("error")
        if isinstance(err, dict) and err.get("message"):
            return str(err["message"])[:400]
        if isinstance(err, str):
            return err[:400]
    except Exception:
        pass
    return (resp.text or "")[:400]


async def _post_chat(
    client: httpx.AsyncClient,
    model: str,
    data_url: str,
    headers: dict[str, str],
) -> httpx.Response:
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": USER_PROMPT},
                    {"type": "image_url", "image_url": {"url": data_url}},
                ],
            },
        ],
        "temperature": 0.2,
        "max_tokens": 200,
    }
    return await client.post(
        f"{settings.openrouter_url}/chat/completions",
        json=payload,
        headers=headers,
    )


async def analyze_portrait(image: Path | tuple[str, bytes]) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    """Send the portrait to the configured model and return (parsed_json, raw_response).

    Behaviour:
      - Exactly one upstream request is in flight at any time (process-wide lock).
      - On HTTP 429, wait either the server's `Retry-After` value or a spaced
        backoff (3s, 8s, 15s) and try again. Up to 3 retries, then give up.
      - No fallback / parallel calls to other models.
      - On final failure, raise StyleAnalysisError with a user-safe message.
    """
    if not settings.OPEN_ROUTER_API_KEY:
        raise StyleAnalysisError(
            "No OpenRouter API key is configured. Add OPEN_ROUTER_API_KEY to the backend .env file and restart the server."
        )

    model = (settings.OPENROUTER_MODEL or "").strip()
    if not model:
        raise StyleAnalysisError("Style analysis is temporarily unavailable.")

    data_url = _portrait_to_data_url(image)

    headers = {
        "Authorization": f"Bearer {settings.OPEN_ROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": settings.OPENROUTER_HTTP_REFERER,
        "X-Title": settings.OPENROUTER_APP_TITLE,
    }

    # First arg = default for read/write/pool; connect gets its own budget (httpx.Timeout rules).
    timeout = httpx.Timeout(
        settings.OPENROUTER_READ_TIMEOUT,
        connect=settings.OPENROUTER_CONNECT_TIMEOUT,
    )
    async with _request_lock, httpx.AsyncClient(
        timeout=timeout,
        follow_redirects=True,
        trust_env=True,
        http2=False,
    ) as client:
        attempt = 0
        max_attempts = 1 + len(RETRY_BACKOFF_SECONDS)
        last_status: int | None = None
        last_kind: str | None = None

        while attempt < max_attempts:
            try:
                resp = await _post_chat(client, model, data_url, headers)
            except httpx.ConnectTimeout as e:
                logger.warning("OpenRouter connect timeout: %r", e)
                raise StyleAnalysisError(
                    "Connecting to OpenRouter timed out. Check your network or VPN, try again, "
                    "or set HTTP_PROXY/HTTPS_PROXY in the environment if you browse through a proxy."
                ) from e
            except httpx.ReadTimeout as e:
                logger.warning("OpenRouter read timeout: %r", e)
                raise StyleAnalysisError(
                    "OpenRouter took too long to answer. Try again in a moment, or use a smaller portrait image."
                ) from e
            except httpx.ConnectError as e:
                logger.warning("OpenRouter connect error: %r", e)
                raise StyleAnalysisError(
                    "Could not reach OpenRouter (connection failed). Confirm you have internet access, "
                    "that https://openrouter.ai is not blocked by firewall or DNS, and restart the API. "
                    "If you use a corporate proxy, configure HTTP_PROXY/HTTPS_PROXY for the backend process."
                ) from e
            except httpx.RequestError as e:
                logger.warning("Network error calling style provider: %r", e)
                msg = (
                    "Could not reach the style service over the network. Check your connection, DNS, "
                    "and try again. If the problem persists, verify the machine running the API can open "
                    "https://openrouter.ai in a browser or with curl."
                )
                errn = getattr(e, "__context__", None) or e
                errn = getattr(errn, "errno", None)
                if errn == -3:
                    msg = (
                        "DNS lookup failed for the style service. Check internet access or try again; "
                        "on some networks you may need to change DNS (e.g. 8.8.8.8) or disable VPN briefly."
                    )
                raise StyleAnalysisError(msg) from e

            last_status = resp.status_code

            if resp.status_code == 200:
                try:
                    data = resp.json()
                except ValueError:
                    raise StyleAnalysisError(
                        "We couldn't read the style response. Please try again."
                    )

                try:
                    content = data["choices"][0]["message"]["content"]
                    if isinstance(content, list):
                        content = "".join(
                            part.get("text", "") for part in content if isinstance(part, dict)
                        )
                except (KeyError, IndexError, TypeError):
                    content = ""

                parsed = _extract_json(content) if isinstance(content, str) else None
                if parsed:
                    return parsed, data
                last_kind = "no_json"
                break

            if resp.status_code == 429:
                if attempt >= len(RETRY_BACKOFF_SECONDS):
                    break
                retry_after = resp.headers.get("retry-after")
                delay = RETRY_BACKOFF_SECONDS[attempt]
                try:
                    if retry_after:
                        delay = max(delay, min(float(retry_after), 30.0))
                except ValueError:
                    pass
                logger.info(
                    "Style provider rate-limited; waiting %.1fs before retry %d/%d",
                    delay,
                    attempt + 1,
                    len(RETRY_BACKOFF_SECONDS),
                )
                await asyncio.sleep(delay)
                attempt += 1
                continue

            detail = _openrouter_error_body(resp)
            logger.error(
                "Style provider HTTP %s | model=%s | attempt=%d | body=%s",
                resp.status_code,
                model,
                attempt + 1,
                detail[:600] if detail else "<empty>",
            )
            if resp.status_code == 401:
                raise StyleAnalysisError(
                    "OpenRouter rejected this API key. Confirm OPEN_ROUTER_API_KEY in your .env "
                    "matches the secret key in your OpenRouter dashboard."
                )
            if resp.status_code in (400, 404):
                raise StyleAnalysisError(
                    "The vision model request failed — check OPENROUTER_MODEL in .env (it must be a "
                    f"valid model id for your account). Details: {detail or 'see server logs.'}"
                )
            raise StyleAnalysisError(
                f"The style service returned HTTP {resp.status_code}. {detail or 'Please try again shortly.'}"
            )

    if last_status == 429:
        raise StyleAnalysisError(
            "Too many style checks in a short time (free service limit), or the "
            "provider is busy. Please wait 3–5 minutes, then try again. "
            "If this keeps happening, add a few dollars of credit on your API "
            "account or use the app a little less often."
        )
    if last_kind == "no_json":
        raise StyleAnalysisError("We couldn't read the portrait clearly. Try a different photo.")

    raise StyleAnalysisError("Style analysis is temporarily unavailable. Please try again.")


RECOMMEND_SYSTEM = (
    "You are a fashion stylist. You receive client context (skin_tone and face_shape are authoritative) "
    "plus numbered garment product images. Each image matches one line in the list (garment_id). "
    "Rank by: colour harmony with skin_tone, neckline/silhouette vs face_shape, and weather practicality. "
    "Return ONLY JSON: "
    '{"selected_garment_id": <int from list>, "reasoning": "<=3 sentences>", "show_recommended": true}'
)


def _extract_json_object(text: str) -> dict[str, Any] | None:
    if not text:
        return None
    start = text.find("{")
    if start < 0:
        return None
    depth = 0
    for i in range(start, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                try:
                    return json.loads(text[start : i + 1])
                except json.JSONDecodeError:
                    return None
    return None


async def _fetch_garment_image_data_url(client: httpx.AsyncClient, url: str) -> str | None:
    from urllib.parse import urlparse

    from .brand_scrape import USER_AGENT

    u = (url or "").strip()
    if not u.startswith("http"):
        return None
    parsed = urlparse(u)
    referer = f"{parsed.scheme}://{parsed.netloc}/"
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "image/*,*/*;q=0.8",
        "Referer": referer,
    }
    try:
        r = await client.get(u, headers=headers)
    except httpx.RequestError:
        return None
    if r.status_code != 200:
        return None
    return _encode_bytes_to_data_url(r.headers.get("content-type", "image/jpeg"), r.content)


async def recommend_catalog_garment(*, session: "UserSession", garments: list["Garment"]) -> dict[str, Any] | None:
    """Gemma 4 (vision) picks one garment from the filtered catalogue."""
    if not settings.OPEN_ROUTER_API_KEY:
        return None
    model = settings.openrouter_catalog_model
    if not model:
        return None

    timeout = httpx.Timeout(max(settings.OPENROUTER_READ_TIMEOUT, 180.0), connect=settings.OPENROUTER_CONNECT_TIMEOUT)
    headers = {
        "Authorization": f"Bearer {settings.OPEN_ROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": settings.OPENROUTER_HTTP_REFERER,
        "X-Title": settings.OPENROUTER_APP_TITLE,
    }

    async with _recommend_lock, httpx.AsyncClient(timeout=timeout, follow_redirects=True, trust_env=True, http2=False) as client:

        async def load(g):
            du = await _fetch_garment_image_data_url(client, g.image_url)
            return (g, du) if du else None

        loaded = [p for p in await asyncio.gather(*(load(g) for g in garments)) if p]
        if len(loaded) < 2:
            logger.warning("Recommend: only %d/%d images loaded", len(loaded), len(garments))
            return None

        lines = [f"{i}. garment_id={g.id}, title={g.title!r}, color={g.color or 'n/a'}" for i, (g, _) in enumerate(loaded, 1)]
        w = session.weather if isinstance(session.weather, dict) else {}
        text = (
            f"Garments (image order = lines 1..{len(lines)}):\n"
            + "\n".join(lines)
            + "\n\nClient (use these values):\n"
            f"skin_tone: {session.skin_tone}\n"
            f"face_shape: {session.face_shape}\n"
            f"occasion: {session.occasion.value if session.occasion else 'n/a'}\n"
            f"event: {session.event.value if session.event else 'n/a'}\n"
            f"style: {session.style.value if session.style else 'n/a'}\n"
            f"gender: {session.gender.value if session.gender else 'n/a'}\n"
            f"city: {session.city or 'n/a'}\n"
            f"weather: {json.dumps(w, ensure_ascii=False)}\n"
        )
        parts: list[dict[str, Any]] = [{"type": "text", "text": text}]
        for _, du in loaded:
            parts.append({"type": "image_url", "image_url": {"url": du}})

        try:
            resp = await client.post(
                f"{settings.openrouter_url}/chat/completions",
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": RECOMMEND_SYSTEM},
                        {"role": "user", "content": parts},
                    ],
                    "temperature": 0.25,
                    "max_tokens": 700,
                },
                headers=headers,
            )
        except httpx.RequestError as e:
            logger.warning("Recommend request failed: %s", e)
            return None

        if resp.status_code != 200:
            logger.warning("Recommend HTTP %s: %s", resp.status_code, _openrouter_error_body(resp)[:200])
            return None

        try:
            content = resp.json()["choices"][0]["message"]["content"]
            if isinstance(content, list):
                content = "".join(p.get("text", "") for p in content if isinstance(p, dict))
        except (KeyError, IndexError, TypeError, ValueError):
            content = ""

        if not isinstance(content, str):
            return None
        parsed = _extract_json_object(content)
        if isinstance(parsed, dict):
            return parsed
        m = re.search(r'"selected_garment_id"\s*:\s*(\d+)', content)
        if m:
            return {"selected_garment_id": int(m.group(1)), "reasoning": "", "show_recommended": True}
        return None
