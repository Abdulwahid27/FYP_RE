from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from typing import Optional, Literal


GenderLiteral = Literal["male", "female"]
OccasionLiteral = Literal["social", "traditional"]
EventLiteral = Literal["office_wear", "hangouts", "religious", "family_gatherings"]
StyleLiteral = Literal["eastern", "western"]


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
    event: EventLiteral
    style: StyleLiteral
    image_url: str
    product_url: Optional[str] = None
    product_type: Optional[str] = None
    tags: Optional[str] = None
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
    event: EventLiteral
    style: StyleLiteral


class ContextOut(BaseModel):
    session_id: int
    weather: Optional[WeatherOut] = None


class RecommendIn(BaseModel):
    session_id: int


class RecommendOut(BaseModel):
    recommended_garment_id: Optional[int] = None
    reasoning: Optional[str] = None
    show_recommended: bool = False


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
    user_id: Optional[int] = None
    created_at: datetime
    skin_tone: Optional[str] = None
    face_shape: Optional[str] = None
    gender: Optional[GenderLiteral] = None
    city: Optional[str] = None
    occasion: Optional[OccasionLiteral] = None
    event: Optional[EventLiteral] = None
    style: Optional[StyleLiteral] = None
    selected_garment_id: Optional[int] = None
    portrait_url: Optional[str] = None
    tryon_url: Optional[str] = None


class RegisterIn(BaseModel):
    full_name: str = Field(min_length=2, max_length=200)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    birth_date: Optional[date] = None

    @field_validator("full_name")
    @classmethod
    def normalize_full_name(cls, v: str) -> str:
        s = " ".join((v or "").split())
        if len(s) < 2:
            raise ValueError("Full name must be at least 2 characters")
        if "@" in s:
            raise ValueError("Use your real name in Full name, not an email address")
        return s

    @field_validator("birth_date", mode="before")
    @classmethod
    def coerce_birth_date(cls, v):
        if v is None or v == "":
            return None
        if isinstance(v, date):
            return v
        if isinstance(v, str):
            t = v.strip()
            if not t:
                return None
            if "T" in t:
                t = t.split("T", 1)[0]
            return date.fromisoformat(t)
        return v


class RegisterOkOut(BaseModel):
    message: str
    email: str


class LoginIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: int
    email: str
    full_name: str
    birth_date: Optional[date] = None
    age: Optional[int] = None


class CityOut(BaseModel):
    name: str
    label: str
