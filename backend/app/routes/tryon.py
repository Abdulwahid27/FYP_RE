import logging
import os
import tempfile
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user
from ..models import Garment, User, UserSession
from ..schemas import TryOnIn, TryOnOut
from ..services.rembg_service import extract_garment_bytes
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


def _suffix_for_mime(mime: str | None) -> str:
    m = (mime or "image/jpeg").split(";")[0].strip().lower()
    return {
        "image/jpeg": ".jpg",
        "image/jpg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp",
    }.get(m, ".jpg")


@router.post("/tryon", response_model=TryOnOut)
async def tryon(
    payload: TryOnIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    session = db.get(UserSession, payload.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed to use this session")
    if not session.portrait_data:
        raise HTTPException(
            status_code=400,
            detail="This session has no portrait in the database. Upload and analyze again.",
        )

    garment = db.get(Garment, payload.garment_id)
    if not garment:
        raise HTTPException(status_code=404, detail="Garment not found")

    cleanup_paths: list[Path] = []
    person_path: Path
    extracted: Path

    try:
        suf = _suffix_for_mime(session.portrait_mime)
        fd, name = tempfile.mkstemp(suffix=suf)
        os.close(fd)
        person_path = Path(name)
        person_path.write_bytes(session.portrait_data)
        cleanup_paths.append(person_path)

        if garment.extracted_data:
            fd, gname = tempfile.mkstemp(suffix=".png")
            os.close(fd)
            extracted = Path(gname)
            extracted.write_bytes(garment.extracted_data)
            cleanup_paths.append(extracted)
        else:
            extracted_bytes = await extract_garment_bytes(garment.image_url)
            garment.extracted_data = extracted_bytes
            garment.extracted_mime = "image/png"
            db.commit()
            fd, gname = tempfile.mkstemp(suffix=".png")
            os.close(fd)
            extracted = Path(gname)
            extracted.write_bytes(extracted_bytes)
            cleanup_paths.append(extracted)

        fd, out_name = tempfile.mkstemp(suffix=".png")
        os.close(fd)
        out_path = Path(out_name)
        cleanup_paths.append(out_path)

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
        session.tryon_data = result_path.read_bytes()
        session.tryon_mime = "image/png"
        db.commit()

    finally:
        for p in cleanup_paths:
            try:
                if p.exists():
                    p.unlink()
            except OSError:
                pass

    return TryOnOut(
        session_id=session.id,
        tryon_url=f"/api/sessions/{session.id}/tryon",
        garment_extracted_url=f"/api/garments/{garment.id}/extracted",
    )
