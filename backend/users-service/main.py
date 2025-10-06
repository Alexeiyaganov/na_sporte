# backend/users-service/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import json
from datetime import datetime
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Users Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Временное хранилище (в продакшене заменить на базу данных)
users_storage = {}
contact_requests = {}


class UserLocation(BaseModel):
    user_id: int
    username: Optional[str] = None
    lat: float
    lng: float
    comment: Optional[str] = None
    sports: Optional[List[str]] = None


class ContactRequest(BaseModel):
    from_user_id: int
    to_user_id: int


@app.get("/")
async def root():
    return {"message": "Users Service is running", "version": "1.0.0"}


@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.post("/api/users/location")
async def update_user_location(location: UserLocation):
    """
    Обновить местоположение пользователя
    """
    logger.info(f"Updating location for user {location.user_id}")

    try:
        users_storage[location.user_id] = {
            "user_id": location.user_id,
            "username": location.username,
            "lat": location.lat,
            "lng": location.lng,
            "comment": location.comment,
            "sports": location.sports or [],
            "last_seen": datetime.now().isoformat(),
            "is_visible": True
        }

        logger.info(f"User {location.user_id} location updated successfully")
        return {"status": "success", "message": "Location updated"}

    except Exception as e:
        logger.error(f"Error updating location: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/api/users/nearby")
async def get_nearby_users(lat: float, lng: float, radius: int = 10):
    """
    Получить пользователей поблизости
    """
    logger.info(f"Finding users near lat={lat}, lng={lng}, radius={radius}km")

    try:
        nearby_users = []

        for user_id, user_data in users_storage.items():
            # Проверяем, что пользователь видим и данные актуальны (последние 2 часа)
            last_seen = datetime.fromisoformat(user_data["last_seen"])
            time_diff = datetime.now() - last_seen
            if time_diff.total_seconds() > 7200:  # 2 часа
                continue

            if not user_data.get("is_visible", True):
                continue

            # Проверяем расстояние
            distance = calculate_distance(lat, lng, user_data["lat"], user_data["lng"])
            if distance <= radius:
                nearby_users.append({
                    "id": user_data["user_id"],
                    "name": user_data["username"] or f"User_{user_data['user_id']}",
                    "lat": user_data["lat"],
                    "lng": user_data["lng"],
                    "comment": user_data["comment"],
                    "sports": user_data["sports"],
                    "distance": round(distance, 2)
                })

        logger.info(f"Found {len(nearby_users)} nearby users")
        return nearby_users

    except Exception as e:
        logger.error(f"Error finding nearby users: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/api/users/contact-request")
async def send_contact_request(request: ContactRequest):
    """
    Отправить запрос на контакт
    """
    logger.info(f"Contact request from {request.from_user_id} to {request.to_user_id}")

    try:
        # Сохраняем запрос
        request_id = f"{request.from_user_id}_{request.to_user_id}"
        contact_requests[request_id] = {
            "from_user_id": request.from_user_id,
            "to_user_id": request.to_user_id,
            "status": "pending",
            "created_at": datetime.now().isoformat()
        }

        logger.info(f"Contact request {request_id} created")
        return {"status": "success", "message": "Contact request sent"}

    except Exception as e:
        logger.error(f"Error sending contact request: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/api/users/{user_id}")
async def get_user_profile(user_id: int):
    """
    Получить профиль пользователя
    """
    if user_id not in users_storage:
        raise HTTPException(status_code=404, detail="User not found")

    user_data = users_storage[user_id]
    return {
        "id": user_data["user_id"],
        "username": user_data["username"],
        "comment": user_data["comment"],
        "sports": user_data["sports"]
    }


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Упрощенный расчет расстояния между точками (в км)
    """
    return ((lat1 - lat2) ** 2 + (lon1 - lon2) ** 2) ** 0.5 * 111


# Запуск приложения
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8002, reload=True)