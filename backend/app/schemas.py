from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import Any, Optional, Literal


GenderLiteral = Literal["male", "female"]
OccasionLiteral = Literal["wedding", "casual", "office", "party"]


class BrandOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str
    description: Optional[str] = None
    logo_url: Optional[str] = None
    website: Optional[str] = None


class GarmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    brand_id: int
    title: str
    gender: GenderLiteral
    occasion: OccasionLiteral
    image_url: str
    price: Optional[str] = None
    color: Optional[str] = None


class AnalyzeOut(BaseModel):
    session_id: int
    skin_tone: Optional[str] = None
    face_shape: Optional[str] = None
    portrait_url: str
    raw: Optional[dict] = None


class WeatherOut(BaseModel):
    city: str
    country: Optional[str] = None
    temperature_c: Optional[float] = None
    feels_like_c: Optional[float] = None
    humidity: Optional[int] = None
    description: Optional[str] = None
    icon: Optional[str] = None


class ContextIn(BaseModel):
    session_id: int
    gender: GenderLiteral
    city: str
    occasion: OccasionLiteral
    brand_id: Optional[int] = None


class ContextOut(BaseModel):
    session_id: int
    weather: Optional[WeatherOut] = None


class TryOnIn(BaseModel):
    session_id: int
    garment_id: int


class TryOnOut(BaseModel):
    session_id: int
    tryon_url: str
    garment_extracted_url: str


class SessionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    skin_tone: Optional[str] = None
    face_shape: Optional[str] = None
    gender: Optional[GenderLiteral] = None
    city: Optional[str] = None
    occasion: Optional[OccasionLiteral] = None
    brand_id: Optional[int] = None
    selected_garment_id: Optional[int] = None
    portrait_url: Optional[str] = None
    tryon_url: Optional[str] = None


class CityOut(BaseModel):
    name: str
    label: str
