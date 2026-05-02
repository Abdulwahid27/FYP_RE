import asyncio
import base64
import json
import logging
import re
from pathlib import Path
from typing import Any

import httpx

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


async def analyze_portrait(image_path: Path) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    """Send the portrait to the configured model and return (parsed_json, raw_response).

    Behaviour:
      - Exactly one upstream request is in flight at any time (process-wide lock).
      - On HTTP 429, wait either the server's `Retry-After` value or a spaced
        backoff (3s, 8s, 15s) and try again. Up to 3 retries, then give up.
      - No fallback / parallel calls to other models.
      - On final failure, raise StyleAnalysisError with a user-safe message.
    """
    if not settings.OPEN_ROUTER_API_KEY:
        raise StyleAnalysisError("Style analysis is temporarily unavailable.")

    model = (settings.OPENROUTER_MODEL or "").strip()
    if not model:
        raise StyleAnalysisError("Style analysis is temporarily unavailable.")

    data_url = _encode_image_to_data_url(image_path)

    headers = {
        "Authorization": f"Bearer {settings.OPEN_ROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:5173",
        "X-Title": "Atelier",
    }

    async with _request_lock, httpx.AsyncClient(timeout=120) as client:
        attempt = 0
        max_attempts = 1 + len(RETRY_BACKOFF_SECONDS)
        last_status: int | None = None
        last_kind: str | None = None

        while attempt < max_attempts:
            try:
                resp = await _post_chat(client, model, data_url, headers)
            except httpx.RequestError as e:
                # Log full context so "couldn't reach" in logs is diagnosable (DNS vs timeout vs SSL).
                logger.warning("Network error calling style provider: %r", e)
                msg = "Couldn't reach the style service. Check your connection and retry."
                errn = getattr(e, "__context__", None) or e
                errn = getattr(errn, "errno", None)
                if errn == -3:  # socket.EAI_AGAIN: DNS / transient name resolution failure
                    msg = (
                        "The style service couldn't be reached (network or DNS). "
                        "Check internet access, or restart the app from a normal terminal if you're developing locally."
                    )
                raise StyleAnalysisError(msg)

            last_status = resp.status_code

            if resp.status_code != 200:
                body_preview = resp.text[:600] if resp.text else "<empty body>"
                logger.error(
                    "Style provider HTTP %s | model=%s | attempt=%d | body=%s",
                    resp.status_code,
                    model,
                    attempt + 1,
                    body_preview,
                )

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

            # Non-429 error — don't keep retrying, fail clearly.
            logger.warning("Style provider returned %s", resp.status_code)
            break

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
