from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session
from sqlalchemy import select

from ..database import get_db
from ..deps import get_current_user
from ..models import User, UserSession
from ..schemas import SessionOut


router = APIRouter(prefix="/api", tags=["sessions"])


def _portrait_url(session: UserSession) -> str | None:
    if session.portrait_data is not None:
        return f"/api/sessions/{session.id}/portrait"
    return None


def _tryon_url(session: UserSession) -> str | None:
    if session.tryon_data is not None:
        return f"/api/sessions/{session.id}/tryon"
    return None


def _hydrate(session: UserSession) -> SessionOut:
    return SessionOut(
        id=session.id,
        user_id=session.user_id,
        created_at=session.created_at,
        skin_tone=session.skin_tone,
        face_shape=session.face_shape,
        gender=session.gender.value if session.gender else None,
        city=session.city,
        occasion=session.occasion.value if session.occasion else None,
        event=session.event.value if session.event else None,
        style=session.style.value if session.style else None,
        selected_garment_id=session.selected_garment_id,
        portrait_url=_portrait_url(session),
        tryon_url=_tryon_url(session),
    )


def _require_session_owner(session: UserSession | None, user: User) -> UserSession:
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.user_id is None or session.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not allowed to access this session")
    return session


@router.get("/sessions", response_model=list[SessionOut])
def list_sessions(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    rows = (
        db.execute(
            select(UserSession)
            .where(UserSession.user_id == current_user.id)
            .order_by(UserSession.created_at.desc())
            .limit(50)
        )
        .scalars()
        .all()
    )
    return [_hydrate(r) for r in rows]


@router.get("/sessions/{session_id}", response_model=SessionOut)
def get_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    s = db.get(UserSession, session_id)
    _require_session_owner(s, current_user)
    return _hydrate(s)


@router.get("/sessions/{session_id}/portrait")
def get_session_portrait(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    s = db.get(UserSession, session_id)
    _require_session_owner(s, current_user)
    if s.portrait_data is not None:
        return Response(
            content=s.portrait_data,
            media_type=s.portrait_mime or "image/jpeg",
            headers={"Cache-Control": "private, max-age=3600"},
        )
    raise HTTPException(status_code=404, detail="Portrait not found")


@router.get("/sessions/{session_id}/tryon")
def get_session_tryon(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    s = db.get(UserSession, session_id)
    _require_session_owner(s, current_user)
    if s.tryon_data is not None:
        return Response(
            content=s.tryon_data,
            media_type=s.tryon_mime or "image/png",
            headers={"Cache-Control": "private, max-age=3600"},
        )
    raise HTTPException(status_code=404, detail="Try-on result not found")
