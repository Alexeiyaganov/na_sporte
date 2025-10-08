# flask_app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Хранилище данных
users_storage = {}

# Mock данные мероприятий
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
    },
    {
        "id": 3, "title": "Открытие лыжного сезона", "sport": "лыжи",
        "description": "Групповая лыжная прогулка с инструкторами",
        "date": "2024-12-10", "location": "Москва, Крылатское",
        "lat": 55.756, "lng": 37.438
    }
]


@app.route('/')
def root():
    return jsonify({"message": "SportEvents API is running on PythonAnywhere", "status": "success"})


@app.route('/health')
def health():
    return jsonify({"status": "healthy", "services": ["events", "users"]})


@app.route('/api/events', methods=['GET'])
def get_events():
    """API мероприятий"""
    try:
        sport = request.args.get('sport')
        lat = request.args.get('lat', type=float)
        lng = request.args.get('lng', type=float)
        radius = request.args.get('radius', type=int)

        events = MOCK_EVENTS.copy()

        if sport:
            events = [e for e in events if e['sport'] == sport]

        if lat and lng and radius:
            events = [e for e in events if calculate_distance(lat, lng, e['lat'], e['lng']) <= radius]

        return jsonify({"status": "success", "data": events})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/users/location', methods=['POST'])
def update_user_location():
    """Обновить местоположение пользователя"""
    try:
        data = request.get_json()

        users_storage[data['user_id']] = {
            "user_id": data['user_id'],
            "username": data.get('username'),
            "lat": data['lat'],
            "lng": data['lng'],
            "comment": data.get('comment'),
            "sports": data.get('sports', []),
            "last_seen": datetime.now().isoformat(),
            "is_visible": True
        }

        return jsonify({"status": "success", "message": "Location updated"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/users/nearby', methods=['GET'])
def get_nearby_users():
    """Получить пользователей поблизости"""
    try:
        lat = request.args.get('lat', type=float)
        lng = request.args.get('lng', type=float)
        radius = request.args.get('radius', default=10, type=int)

        if not lat or not lng:
            return jsonify({"status": "error", "message": "Lat and lng parameters required"}), 400

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

        return jsonify({"status": "success", "data": nearby_users})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


def calculate_distance(lat1, lon1, lat2, lon2):
    """Расчет расстояния между точками (в км)"""
    return ((lat1 - lat2) ** 2 + (lon1 - lon2) ** 2) ** 0.5 * 111


if __name__ == "__main__":
    app.run(debug=True)