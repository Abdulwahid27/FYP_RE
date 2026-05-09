import asyncio

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user
from ..models import User, UserSession
from ..schemas import AnalyzeOut
from ..services.openrouter import analyze_portrait, StyleAnalysisError


router = APIRouter(prefix="/api", tags=["analysis"])


ALLOWED_TYPES = {"image/jpeg", "image/jpg", "image/png", "image/webp"}


@router.post("/analyze", response_model=AnalyzeOut)
async def analyze(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Only JPEG/PNG/WEBP images are allowed")

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Empty file")

    mime = (file.content_type or "image/jpeg").split(";")[0].strip().lower()

    # Cancel the upstream LLM call as soon as the client disconnects (Stop button / tab close).
    analyze_task = asyncio.create_task(analyze_portrait((mime, content)))

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
        user_id=current_user.id,
        portrait_data=content,
        portrait_mime=mime,
        skin_tone=skin_tone,
        face_shape=face_shape,
        analysis_raw={"parsed": parsed, "model_response_keys": list(raw.keys()) if isinstance(raw, dict) else []},
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    # Relative path: SPA loads via Vite proxy or prefixes VITE_API_BASE in fetch/img helpers.
    portrait_url = f"/api/sessions/{session.id}/portrait"

    return AnalyzeOut(
        session_id=session.id,
        skin_tone=skin_tone,
        face_shape=face_shape,
        portrait_url=portrait_url,
        raw=parsed,
    )
