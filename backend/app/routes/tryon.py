import logging
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from ..config import settings
from ..database import get_db
from ..models import Garment, UserSession
from ..schemas import TryOnIn, TryOnOut
from ..services.rembg_service import extract_garment
from ..services.vton import run_virtual_tryon


router = APIRouter(prefix="/api", tags=["tryon"])
logger = logging.getLogger(__name__)


def _friendly_vton_error(exc: BaseException) -> tuple[int, str]:
    """Map upstream HF Space errors to status + user-safe detail (no Gradio/ZeroGPU jargon)."""
    msg = str(exc).lower()
    if "zerogpu" in msg or ("quota" in msg and "daily" in msg):
        return (
            503,
            "The fitting service has reached its daily free limit. Try again tomorrow, "
            "or link a Hugging Face account with a Pro / paid plan for more capacity.",
        )
    if "out of" in msg and "quota" in msg:
        return (
            503,
            "The fitting service is temporarily at capacity. Please try again in a few hours.",
        )
    return (502, "The fitting could not be completed. Please try again in a few minutes.")


def _abs_from_rel(rel: str) -> Path:
    return (settings.UPLOAD_DIR.parent / rel).resolve()


@router.post("/tryon", response_model=TryOnOut)
async def tryon(payload: TryOnIn, request: Request, db: Session = Depends(get_db)):
    session = db.get(UserSession, payload.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if not session.portrait_path:
        raise HTTPException(status_code=400, detail="Session has no portrait")

    garment = db.get(Garment, payload.garment_id)
    if not garment:
        raise HTTPException(status_code=404, detail="Garment not found")

    if garment.extracted_path:
        extracted = _abs_from_rel(garment.extracted_path)
        if not extracted.exists():
            extracted = None
    else:
        extracted = None

    if extracted is None:
        out_name = f"{uuid.uuid4().hex}.png"
        out_path = settings.GARMENTS_DIR / out_name
        try:
            extracted = await extract_garment(garment.image_url, out_path)
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"Garment extraction failed: {e}")

        garment.extracted_path = str(extracted.relative_to(settings.UPLOAD_DIR.parent))
        db.commit()

    person_path = _abs_from_rel(session.portrait_path)
    if not person_path.exists():
        raise HTTPException(status_code=400, detail="Original portrait not found on disk")

    out_name = f"{uuid.uuid4().hex}.png"
    out_path = settings.TRYONS_DIR / out_name
    try:
        result_path = await run_virtual_tryon(
            person_image=person_path,
            garment_image=extracted,
            out_path=out_path,
            garment_desc=garment.title,
        )
    except Exception as e:
        logger.exception("Virtual try-on failed")
        code, detail = _friendly_vton_error(e)
        raise HTTPException(status_code=code, detail=detail)

    session.selected_garment_id = garment.id
    session.tryon_path = str(result_path.relative_to(settings.UPLOAD_DIR.parent))
    db.commit()

    base = str(request.base_url).rstrip("/")
    rel_garment = Path(garment.extracted_path).as_posix()
    rel_tryon = Path(session.tryon_path).as_posix()

    return TryOnOut(
        session_id=session.id,
        tryon_url=f"{base}/{rel_tryon}",
        garment_extracted_url=f"{base}/{rel_garment}",
    )
