from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy import select

from ..database import get_db
from ..models import UserSession
from ..schemas import SessionOut


router = APIRouter(prefix="/api", tags=["sessions"])


def _hydrate(session: UserSession, base_url: str) -> SessionOut:
    portrait_url = f"{base_url}/{session.portrait_path}" if session.portrait_path else None
    tryon_url = f"{base_url}/{session.tryon_path}" if session.tryon_path else None
    return SessionOut(
        id=session.id,
        created_at=session.created_at,
        skin_tone=session.skin_tone,
        face_shape=session.face_shape,
        gender=session.gender.value if session.gender else None,
        city=session.city,
        occasion=session.occasion.value if session.occasion else None,
        brand_id=session.brand_id,
        selected_garment_id=session.selected_garment_id,
        portrait_url=portrait_url,
        tryon_url=tryon_url,
    )


@router.get("/sessions", response_model=list[SessionOut])
def list_sessions(request: Request, db: Session = Depends(get_db)):
    base = str(request.base_url).rstrip("/")
    rows = (
        db.execute(select(UserSession).order_by(UserSession.created_at.desc()).limit(50))
        .scalars()
        .all()
    )
    return [_hydrate(r, base) for r in rows]


@router.get("/sessions/{session_id}", response_model=SessionOut)
def get_session(session_id: int, request: Request, db: Session = Depends(get_db)):
    base = str(request.base_url).rstrip("/")
    s = db.get(UserSession, session_id)
    if not s:
        raise HTTPException(status_code=404, detail="Session not found")
    return _hydrate(s, base)
