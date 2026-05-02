from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import UserSession, Gender, Occasion
from ..schemas import ContextIn, ContextOut, WeatherOut, CityOut
from ..services.weather import get_weather, PAKISTAN_CITIES


router = APIRouter(prefix="/api", tags=["context"])


@router.get("/cities", response_model=list[CityOut])
def cities():
    return PAKISTAN_CITIES


@router.get("/weather", response_model=WeatherOut)
async def weather(city: str):
    data = await get_weather(city)
    if not data:
        raise HTTPException(status_code=404, detail="Weather unavailable for this city")
    return data


@router.post("/context", response_model=ContextOut)
async def set_context(payload: ContextIn, db: Session = Depends(get_db)):
    session = db.get(UserSession, payload.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    weather_data = await get_weather(payload.city)

    session.gender = Gender(payload.gender)
    session.city = payload.city
    session.occasion = Occasion(payload.occasion)
    session.brand_id = payload.brand_id
    session.weather = weather_data

    db.commit()
    db.refresh(session)

    return ContextOut(
        session_id=session.id,
        weather=WeatherOut(**weather_data) if weather_data else None,
    )
