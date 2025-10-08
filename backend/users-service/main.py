# backend/users-service/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Users Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

users_storage = {}


class UserLocation(BaseModel):
    user_id: int
    username: Optional[str] = None
    lat: float
    lng: float
    comment: Optional[str] = None
    sports: Optional[List[str]] = None


@app.get("/")
async def root():
    return {"message": "Users Service is running"}


@app.post("/api/users/location")
async def update_user_location(location: UserLocation):
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
    return {"status": "success", "message": "Location updated"}


@app.get("/api/users/nearby")
async def get_nearby_users(lat: float, lng: float, radius: int = 10):
    nearby_users = []

    for user_id, user_data in users_storage.items():
        last_seen = datetime.fromisoformat(user_data["last_seen"])
        time_diff = datetime.now() - last_seen
        if time_diff.total_seconds() > 7200:  # 2 часа
            continue

        if not user_data.get("is_visible", True):
            continue

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

    return nearby_users


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    return ((lat1 - lat2) ** 2 + (lon1 - lon2) ** 2) ** 0.5 * 111


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8080))  # Fly.io использует 8080
    uvicorn.run(app, host="0.0.0.0", port=port)