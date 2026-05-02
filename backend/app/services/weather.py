import httpx

from ..config import settings


PAKISTAN_CITIES = [
    {"name": "Karachi", "label": "Karachi"},
    {"name": "Lahore", "label": "Lahore"},
    {"name": "Islamabad", "label": "Islamabad"},
    {"name": "Rawalpindi", "label": "Rawalpindi"},
    {"name": "Faisalabad", "label": "Faisalabad"},
    {"name": "Multan", "label": "Multan"},
    {"name": "Peshawar", "label": "Peshawar"},
    {"name": "Quetta", "label": "Quetta"},
    {"name": "Hyderabad", "label": "Hyderabad"},
    {"name": "Sialkot", "label": "Sialkot"},
    {"name": "Gujranwala", "label": "Gujranwala"},
    {"name": "Bahawalpur", "label": "Bahawalpur"},
    {"name": "Sargodha", "label": "Sargodha"},
    {"name": "Sukkur", "label": "Sukkur"},
    {"name": "Abbottabad", "label": "Abbottabad"},
]


async def get_weather(city: str) -> dict | None:
    if not settings.OPENWEATHER_API_KEY:
        return None
    params = {
        "q": f"{city},PK",
        "appid": settings.OPENWEATHER_API_KEY,
        "units": "metric",
    }
    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.get(settings.OPENWEATHER_BASE_URL, params=params)
        if resp.status_code != 200:
            return None
        data = resp.json()

    weather0 = (data.get("weather") or [{}])[0]
    main = data.get("main") or {}
    return {
        "city": data.get("name", city),
        "country": (data.get("sys") or {}).get("country"),
        "temperature_c": main.get("temp"),
        "feels_like_c": main.get("feels_like"),
        "humidity": main.get("humidity"),
        "description": weather0.get("description"),
        "icon": weather0.get("icon"),
    }
