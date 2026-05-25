from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user
from ..models import User, UserSession, Gender, Occasion, Event, Style, EVENT_OCCASION
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
async def set_context(
    payload: ContextIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    session = db.get(UserSession, payload.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed to update this session")

    try:
        occasion = Occasion(payload.occasion)
        event = Event(payload.event)
        style = Style(payload.style)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid occasion, event, or style")

    if EVENT_OCCASION.get(event) is not occasion:
        raise HTTPException(
            status_code=400,
            detail=f"Event '{event.value}' does not belong to occasion '{occasion.value}'.",
        )

    weather_data = await get_weather(payload.city)

    session.gender = Gender(payload.gender)
    session.city = payload.city
    session.occasion = occasion
    session.event = event
    session.style = style
    session.weather = weather_data

    db.commit()
    db.refresh(session)

    return ContextOut(
        session_id=session.id,
        weather=WeatherOut(**weather_data) if weather_data else None,
    )
