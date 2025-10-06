# backend/events-service/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import json
from datetime import datetime
import logging
from typing import List, Optional

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Events Service", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock данные мероприятий
MOCK_EVENTS = [
    {
        "id": 1,
        "title": "Московский марафон 2024",
        "description": "Ежегодный осенний марафон через центр Москвы. Дистанции: 10км, 21.1км, 42.2км",
        "sport": "бег",
        "date": "2024-09-15",
        "location": "Москва, Воробьевы горы",
        "lat": 55.710,
        "lng": 37.553
    },
    {
        "id": 2,
        "title": "Ночной велопробег",
        "description": "Ночная велопрогулка по освещенным улицам города. Безопасность обеспечивается организаторами",
        "sport": "велоспорт",
        "date": "2024-10-20",
        "location": "Москва, Парк Горького",
        "lat": 55.731,
        "lng": 37.603
    },
    {
        "id": 3,
        "title": "Открытие лыжного сезона в Крылатском",
        "description": "Групповая лыжная прогулка с инструкторами. Прокат оборудования доступен на месте",
        "sport": "лыжи",
        "date": "2024-12-10",
        "location": "Москва, Крылатское",
        "lat": 55.756,
        "lng": 37.438
    },
    {
        "id": 4,
        "title": "Утренняя йога в Сокольниках",
        "description": "Бесплатное занятие йогой на свежем воздухе. Приносите свои коврики!",
        "sport": "йога",
        "date": "2024-08-25",
        "location": "Москва, Сокольники",
        "lat": 55.795,
        "lng": 37.679
    }
]


@app.get("/")
async def root():
    return {"message": "Events Service is running", "version": "1.0.0"}


@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.get("/api/events")
async def get_events(sport: Optional[str] = None, lat: Optional[float] = None, lng: Optional[float] = None,
                     radius: Optional[int] = None):
    """
    Получить мероприятия с возможностью фильтрации
    """
    logger.info(f"Fetching events with filters: sport={sport}, lat={lat}, lng={lng}, radius={radius}")

    events = MOCK_EVENTS.copy()

    # Фильтрация по виду спорта
    if sport:
        events = [e for e in events if e['sport'] == sport]

    # Фильтрация по расстоянию
    if lat and lng and radius:
        events = [e for e in events if calculate_distance(lat, lng, e['lat'], e['lng']) <= radius]

    logger.info(f"Returning {len(events)} events")
    return events


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Упрощенный расчет расстояния между точками (в км)
    """
    return ((lat1 - lat2) ** 2 + (lon1 - lon2) ** 2) ** 0.5 * 111


# Запуск приложения
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)