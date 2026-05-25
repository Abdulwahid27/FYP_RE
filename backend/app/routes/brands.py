import logging
from urllib.parse import urlparse

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..config import settings
from ..database import get_db
from ..deps import get_current_user
from ..models import Brand, Garment, Gender, Event, Style, User, UserSession
from ..schemas import BrandOut, GarmentOut, RecommendIn, RecommendOut
from ..services.brand_scrape import USER_AGENT
from ..services.catalog_filters import passes_feels_like_filter
from ..services.catalog_fallback import pick_garment_from_catalog_rules
from ..services.openrouter import recommend_catalog_garment


router = APIRouter(prefix="/api", tags=["catalog"])
logger = logging.getLogger(__name__)


def query_garments_filtered(
    db: Session,
    *,
    gender: Gender,
    event: Event,
    style: Style,
    feels_like_c: float | None,
) -> list[Garment]:
    """Same catalogue as step 3 grid: gender × event × style (+ warm-weather knit filter)."""
    stmt = select(Garment).where(
        Garment.gender == gender,
        Garment.event == event,
        Garment.style == style,
    )
    rows = list(db.execute(stmt.order_by(Garment.id.desc())).scalars().all())
    if feels_like_c is None:
        return rows
    return [
        g
        for g in rows
        if passes_feels_like_filter(
            title=g.title,
            product_type=g.product_type,
            tags=g.tags,
            feels_like_c=feels_like_c,
        )
    ]


@router.get("/brands", response_model=list[BrandOut])
def list_brands(db: Session = Depends(get_db)):
    return db.execute(select(Brand).order_by(Brand.name)).scalars().all()


@router.get("/garments", response_model=list[GarmentOut])
def list_garments(
    gender: str = Query(...),
    event: str = Query(...),
    style: str = Query(...),
    feels_like_c: float | None = Query(
        None,
        description="OpenWeather 'feels like' °C — when warm, hides obvious winter knitwear.",
    ),
    db: Session = Depends(get_db),
):
    try:
        g = Gender(gender)
        e = Event(event)
        s = Style(style)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid gender, event, or style")

    return query_garments_filtered(db, gender=g, event=e, style=s, feels_like_c=feels_like_c)


@router.post("/garments/recommend", response_model=RecommendOut)
async def recommend_garment(
    payload: RecommendIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    After step 2: load session (portrait analysis + occasion/event/style + weather from DB),
    take the same filtered garments as the grid, send images + context to Gemma 4, return one pick.
    """
    session = db.get(UserSession, payload.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed to use this session")
    if session.gender is None or session.event is None or session.style is None or session.occasion is None:
        raise HTTPException(status_code=400, detail="Complete step 2 (context) first.")
    if not session.skin_tone or not session.face_shape:
        raise HTTPException(status_code=400, detail="Complete step 1 (portrait analysis) first.")

    feels = None
    if isinstance(session.weather, dict) and session.weather.get("feels_like_c") is not None:
        try:
            feels = float(session.weather["feels_like_c"])
        except (TypeError, ValueError):
            pass

    garments = query_garments_filtered(
        db,
        gender=session.gender,
        event=session.event,
        style=session.style,
        feels_like_c=feels,
    )
    cap = max(1, min(settings.CATALOG_RECOMMEND_MAX_ITEMS, 24))
    garments = garments[:cap]

    if len(garments) == 0:
        return RecommendOut()

    if len(garments) == 1:
        return RecommendOut(
            recommended_garment_id=garments[0].id,
            reasoning="Only one outfit matches your selections — this is our pick for you.",
            show_recommended=True,
        )

    def fallback() -> RecommendOut:
        gid, reason = pick_garment_from_catalog_rules(session, garments)
        return RecommendOut(recommended_garment_id=gid, reasoning=reason, show_recommended=gid is not None)

    try:
        result = await recommend_catalog_garment(session=session, garments=garments)
    except Exception:
        logger.exception("Gemma recommend failed")
        return fallback()

    if not result:
        return fallback()

    gid = result.get("selected_garment_id") or result.get("selected_image_id")
    try:
        gid = int(gid) if gid is not None else None
    except (TypeError, ValueError):
        gid = None

    valid = {g.id for g in garments}
    if gid not in valid:
        return fallback()

    reasoning = result.get("reasoning") or result.get("Reasoning")
    if not isinstance(reasoning, str) or not reasoning.strip():
        reasoning = (
            "Recommended for your skin tone, face shape, and today's weather among these "
            f"{session.occasion.value} / {session.event.value} looks."
        )

    return RecommendOut(
        recommended_garment_id=gid,
        reasoning=reasoning.strip(),
        show_recommended=bool(result.get("show_recommended", True)),
    )


@router.get("/garments/{garment_id}/image", response_class=Response)
async def garment_image_proxy(garment_id: int, db: Session = Depends(get_db)):
    """Serve catalog images through the API so the browser is not blocked by
    brand CDNs (hotlink / Referer) when using localhost:5173."""
    g = db.get(Garment, garment_id)
    if not g:
        raise HTTPException(status_code=404, detail="Garment not found")
    url = (g.image_url or "").strip()
    if not url.startswith("http"):
        raise HTTPException(status_code=400, detail="Invalid stored image URL")

    parsed = urlparse(url)
    referer = f"{parsed.scheme}://{parsed.netloc}/"
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
        "Referer": referer,
    }
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=60.0) as client:
            r = await client.get(url, headers=headers)
    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail=f"Image fetch failed: {e!s}") from e

    if r.status_code != 200:
        raise HTTPException(
            status_code=502, detail="Brand server did not return the image (try re-seed)."
        )

    content_type = r.headers.get("content-type", "image/jpeg")
    if not str(content_type).lower().startswith("image/"):
        content_type = "image/jpeg"
    return Response(
        content=r.content,
        media_type=content_type,
        headers={"Cache-Control": "public, max-age=3600"},
    )


@router.get("/garments/{garment_id}/extracted")
def garment_extracted_cutout(garment_id: int, db: Session = Depends(get_db)):
    """Background-removed garment PNG from DB (populated after first try-on or extraction)."""
    g = db.get(Garment, garment_id)
    if not g:
        raise HTTPException(status_code=404, detail="Garment not found")
    if g.extracted_data is not None:
        return Response(
            content=g.extracted_data,
            media_type=g.extracted_mime or "image/png",
            headers={"Cache-Control": "public, max-age=3600"},
        )
    raise HTTPException(status_code=404, detail="Garment cut-out not available yet")


@router.get("/garments/{garment_id}", response_model=GarmentOut)
def get_garment(garment_id: int, db: Session = Depends(get_db)):
    g = db.get(Garment, garment_id)
    if not g:
        raise HTTPException(status_code=404, detail="Garment not found")
    return g
