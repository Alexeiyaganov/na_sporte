from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Events Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

MOCK_EVENTS = [
    {
        "id": 1, "title": "Московский марафон 2024", "sport": "бег",
        "description": "Ежегодный осенний марафон через центр Москвы",
        "date": "2024-09-15", "location": "Москва, Воробьевы горы",
        "lat": 55.710, "lng": 37.553
    },
    {
        "id": 2, "title": "Ночной велопробег", "sport": "велоспорт",
        "description": "Ночная велопрогулка по освещенным улицам города",
        "date": "2024-10-20", "location": "Москва, Парк Горького",
        "lat": 55.731, "lng": 37.603
    }
]


@app.get("/")
async def root():
    return {"message": "Events Service is running on Railway"}


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "events"}


@app.get("/api/events")
async def get_events(sport: str = None, lat: float = None, lng: float = None, radius: int = None):
    events = MOCK_EVENTS.copy()

    if sport:
        events = [e for e in events if e['sport'] == sport]

    if lat and lng and radius:
        events = [e for e in events if calculate_distance(lat, lng, e['lat'], e['lng']) <= radius]

    return events


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    return ((lat1 - lat2) ** 2 + (lon1 - lon2) ** 2) ** 0.5 * 111


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)