from datetime import date, datetime
from sqlalchemy import String, ForeignKey, DateTime, Date, Text, JSON, Enum, LargeBinary
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from .database import Base


class Gender(str, enum.Enum):
    male = "male"
    female = "female"


class Occasion(str, enum.Enum):
    social = "social"
    traditional = "traditional"


class Event(str, enum.Enum):
    office_wear = "office_wear"
    hangouts = "hangouts"
    religious = "religious"
    family_gatherings = "family_gatherings"


class Style(str, enum.Enum):
    eastern = "eastern"
    western = "western"


# Each event belongs to exactly one occasion. Used for validation + UI cascade.
EVENT_OCCASION: dict[Event, Occasion] = {
    Event.office_wear: Occasion.social,
    Event.hangouts: Occasion.social,
    Event.religious: Occasion.traditional,
    Event.family_gatherings: Occasion.traditional,
}


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str] = mapped_column(String(200), default="")
    birth_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    sessions: Mapped[list["UserSession"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )


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
    event: Mapped[Event] = mapped_column(Enum(Event, name="event_enum"), index=True)
    style: Mapped[Style] = mapped_column(Enum(Style, name="style_enum"), index=True)
    image_url: Mapped[str] = mapped_column(String(700))
    product_url: Mapped[str | None] = mapped_column(String(700), nullable=True)
    product_type: Mapped[str | None] = mapped_column(String(120), nullable=True)
    tags: Mapped[str | None] = mapped_column(String(800), nullable=True)
    price: Mapped[str | None] = mapped_column(String(60), nullable=True)
    color: Mapped[str | None] = mapped_column(String(60), nullable=True)
    extracted_data: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    extracted_mime: Mapped[str | None] = mapped_column(String(64), nullable=True)

    brand: Mapped[Brand] = relationship(back_populates="garments")


class UserSession(Base):
    __tablename__ = "user_sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=True)
    user: Mapped["User | None"] = relationship(back_populates="sessions")

    portrait_data: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    portrait_mime: Mapped[str | None] = mapped_column(String(128), nullable=True)
    skin_tone: Mapped[str | None] = mapped_column(String(80), nullable=True)
    face_shape: Mapped[str | None] = mapped_column(String(80), nullable=True)
    analysis_raw: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    gender: Mapped[Gender | None] = mapped_column(Enum(Gender, name="gender_enum"), nullable=True)
    city: Mapped[str | None] = mapped_column(String(120), nullable=True)
    weather: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    occasion: Mapped[Occasion | None] = mapped_column(Enum(Occasion, name="occasion_enum"), nullable=True)
    event: Mapped[Event | None] = mapped_column(Enum(Event, name="event_enum"), nullable=True)
    style: Mapped[Style | None] = mapped_column(Enum(Style, name="style_enum"), nullable=True)

    selected_garment_id: Mapped[int | None] = mapped_column(ForeignKey("garments.id", ondelete="SET NULL"), nullable=True)
    tryon_data: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    tryon_mime: Mapped[str | None] = mapped_column(String(128), nullable=True)
