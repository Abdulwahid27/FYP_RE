from datetime import datetime
from sqlalchemy import String, Integer, ForeignKey, DateTime, Text, JSON, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from .database import Base


class Gender(str, enum.Enum):
    male = "male"
    female = "female"


class Occasion(str, enum.Enum):
    wedding = "wedding"
    casual = "casual"
    office = "office"
    party = "party"


class Brand(Base):
    __tablename__ = "brands"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    slug: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    logo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    website: Mapped[str | None] = mapped_column(String(500), nullable=True)

    garments: Mapped[list["Garment"]] = relationship(back_populates="brand", cascade="all, delete-orphan")


class Garment(Base):
    __tablename__ = "garments"

    id: Mapped[int] = mapped_column(primary_key=True)
    brand_id: Mapped[int] = mapped_column(ForeignKey("brands.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(200))
    gender: Mapped[Gender] = mapped_column(Enum(Gender, name="gender_enum"), index=True)
    occasion: Mapped[Occasion] = mapped_column(Enum(Occasion, name="occasion_enum"), index=True)
    image_url: Mapped[str] = mapped_column(String(700))
    price: Mapped[str | None] = mapped_column(String(60), nullable=True)
    color: Mapped[str | None] = mapped_column(String(60), nullable=True)
    extracted_path: Mapped[str | None] = mapped_column(String(500), nullable=True)

    brand: Mapped[Brand] = relationship(back_populates="garments")


class UserSession(Base):
    __tablename__ = "user_sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    portrait_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    skin_tone: Mapped[str | None] = mapped_column(String(80), nullable=True)
    face_shape: Mapped[str | None] = mapped_column(String(80), nullable=True)
    analysis_raw: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    gender: Mapped[Gender | None] = mapped_column(Enum(Gender, name="gender_enum"), nullable=True)
    city: Mapped[str | None] = mapped_column(String(120), nullable=True)
    weather: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    occasion: Mapped[Occasion | None] = mapped_column(Enum(Occasion, name="occasion_enum"), nullable=True)
    brand_id: Mapped[int | None] = mapped_column(ForeignKey("brands.id", ondelete="SET NULL"), nullable=True)

    selected_garment_id: Mapped[int | None] = mapped_column(ForeignKey("garments.id", ondelete="SET NULL"), nullable=True)
    tryon_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
