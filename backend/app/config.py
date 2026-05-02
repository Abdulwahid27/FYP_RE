from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent
ROOT_DIR = BASE_DIR.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=[ROOT_DIR / ".env", BASE_DIR / ".env"],
        env_file_encoding="utf-8",
        extra="ignore",
    )

    DATABASE_URL: str = "postgresql://abdul-wahid:fashion@localhost:5432/fashion"

    OPEN_ROUTER_API_KEY: str = ""
    OPENROUTER_MODEL: str = "google/gemma-3-27b-it:free"
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    BASE_URL: str = ""

    @property
    def openrouter_url(self) -> str:
        return (self.BASE_URL or self.OPENROUTER_BASE_URL).rstrip("/")

    HF_TOKEN: str = ""
    VTON_SPACE: str = "yisol/IDM-VTON"

    OPENWEATHER_API_KEY: str = ""
    OPENWEATHER_BASE_URL: str = "https://api.openweathermap.org/data/2.5/weather"

    UPLOAD_DIR: Path = BASE_DIR / "uploads"
    ORIGINALS_DIR: Path = BASE_DIR / "uploads" / "originals"
    GARMENTS_DIR: Path = BASE_DIR / "uploads" / "garments"
    TRYONS_DIR: Path = BASE_DIR / "uploads" / "tryons"

    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


settings = Settings()

for d in (settings.UPLOAD_DIR, settings.ORIGINALS_DIR, settings.GARMENTS_DIR, settings.TRYONS_DIR):
    d.mkdir(parents=True, exist_ok=True)
