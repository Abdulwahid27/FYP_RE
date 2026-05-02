from urllib.parse import urlparse

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Brand, Garment, Gender, Occasion
from ..schemas import BrandOut, GarmentOut
from ..services.brand_scrape import USER_AGENT


router = APIRouter(prefix="/api", tags=["catalog"])


@router.get("/brands", response_model=list[BrandOut])
def list_brands(db: Session = Depends(get_db)):
    return db.execute(select(Brand).order_by(Brand.name)).scalars().all()


@router.get("/garments", response_model=list[GarmentOut])
def list_garments(
    gender: str = Query(...),
    occasion: str = Query(...),
    brand_id: int | None = Query(None),
    db: Session = Depends(get_db),
):
    try:
        g = Gender(gender)
        o = Occasion(occasion)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid gender or occasion")

    stmt = select(Garment).where(Garment.gender == g, Garment.occasion == o)
    if brand_id is not None:
        stmt = stmt.where(Garment.brand_id == brand_id)

    return db.execute(stmt.order_by(Garment.id.desc())).scalars().all()


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


@router.get("/garments/{garment_id}", response_model=GarmentOut)
def get_garment(garment_id: int, db: Session = Depends(get_db)):
    g = db.get(Garment, garment_id)
    if not g:
        raise HTTPException(status_code=404, detail="Garment not found")
    return g
