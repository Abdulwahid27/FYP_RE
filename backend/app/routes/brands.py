from urllib.parse import urlparse

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Brand, Garment, Gender, Event, Style
from ..schemas import BrandOut, GarmentOut
from ..services.brand_scrape import USER_AGENT
from ..services.catalog_filters import passes_feels_like_filter


router = APIRouter(prefix="/api", tags=["catalog"])


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

    stmt = select(Garment).where(
        Garment.gender == g,
        Garment.event == e,
        Garment.style == s,
    )

    rows = db.execute(stmt.order_by(Garment.id.desc())).scalars().all()
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
