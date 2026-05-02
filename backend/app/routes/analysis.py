import asyncio
import uuid
from pathlib import Path

import aiofiles
from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
from sqlalchemy.orm import Session

from ..config import settings
from ..database import get_db
from ..models import UserSession
from ..schemas import AnalyzeOut
from ..services.openrouter import analyze_portrait, StyleAnalysisError


router = APIRouter(prefix="/api", tags=["analysis"])


ALLOWED_TYPES = {"image/jpeg", "image/jpg", "image/png", "image/webp"}


@router.post("/analyze", response_model=AnalyzeOut)
async def analyze(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Only JPEG/PNG/WEBP images are allowed")

    suffix = Path(file.filename or "portrait").suffix.lower() or ".jpg"
    if suffix not in {".jpg", ".jpeg", ".png", ".webp"}:
        suffix = ".jpg"

    filename = f"{uuid.uuid4().hex}{suffix}"
    save_path = settings.ORIGINALS_DIR / filename

    async with aiofiles.open(save_path, "wb") as f:
        content = await file.read()
        await f.write(content)

    # Cancel the upstream LLM call as soon as the client disconnects (Stop button / tab close).
    # This prevents wasted retries against the OpenRouter free-tier quota.
    analyze_task = asyncio.create_task(analyze_portrait(save_path))

    async def _watch_disconnect() -> None:
        while not analyze_task.done():
            if await request.is_disconnected():
                analyze_task.cancel()
                return
            await asyncio.sleep(0.5)

    watcher = asyncio.create_task(_watch_disconnect())
    try:
        parsed, raw = await analyze_task
    except asyncio.CancelledError:
        raise HTTPException(status_code=499, detail="Cancelled by client")
    except StyleAnalysisError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Style analysis is temporarily unavailable. Please try again.",
        )
    finally:
        watcher.cancel()

    skin_tone = (parsed or {}).get("skin_tone")
    face_shape = (parsed or {}).get("face_shape")

    session = UserSession(
        portrait_path=str(save_path.relative_to(settings.UPLOAD_DIR.parent)),
        skin_tone=skin_tone,
        face_shape=face_shape,
        analysis_raw={"parsed": parsed, "model_response_keys": list(raw.keys()) if isinstance(raw, dict) else []},
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    base = str(request.base_url).rstrip("/")
    portrait_url = f"{base}/uploads/originals/{filename}"

    return AnalyzeOut(
        session_id=session.id,
        skin_tone=skin_tone,
        face_shape=face_shape,
        portrait_url=portrait_url,
        raw=parsed,
    )
