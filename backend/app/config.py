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
    OPENROUTER_MODEL: str = "google/gemma-4-26b-a4b-it:free"
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    # Legacy: if set to OpenRouter API root, it is used so existing .env keeps working.
    BASE_URL: str = ""
    # Sent to OpenRouter as HTTP-Referer (some keys are restricted by site URL).
    OPENROUTER_HTTP_REFERER: str = "http://localhost:5173"
    OPENROUTER_APP_TITLE: str = "Atelier"
    # httpx: longer connect helps flaky networks; trust_env picks up HTTP(S)_PROXY if set.
    OPENROUTER_CONNECT_TIMEOUT: float = 35.0
    OPENROUTER_READ_TIMEOUT: float = 120.0

    @property
    def openrouter_url(self) -> str:
        legacy = (self.BASE_URL or "").strip().rstrip("/")
        if legacy and "openrouter.ai" in legacy.lower():
            return legacy
        base = (self.OPENROUTER_BASE_URL or "").strip().rstrip("/")
        return base or "https://openrouter.ai/api/v1"

    HF_TOKEN: str = ""
    VTON_SPACE: str = "yisol/IDM-VTON"

    OPENWEATHER_API_KEY: str = ""
    OPENWEATHER_BASE_URL: str = "https://api.openweathermap.org/data/2.5/weather"

    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"

    # Auth: set JWT_SECRET in production (long random string).
    JWT_SECRET: str = "change-me-in-production-use-openssl-rand-hex-32"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    # When true, /api/health includes boot_id (new each process). The SPA clears stored JWT if
    # boot_id changed — handy for local dev so a uvicorn restart "logs everyone out".
    # Set false behind multiple API replicas (each would have a different boot_id).
    BOOT_TOKEN_INVALIDATION: bool = False

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


settings = Settings()
