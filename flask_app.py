# flask_app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta
import logging
import json

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Хранилища данных
trainings_storage = {}
training_participants = {}
user_locations = {}

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
    }
]

# Рекламные локации для тренировок
PROMOTED_LOCATIONS = [
    {
        "id": "promo_1",
        "title": "🏃 Беговая группа в Парке Горького",
        "description": "Присоединяйтесь к нашей утренней беговой группе!",
        "lat": 55.731,
        "lng": 37.603,
        "sport": "бег",
        "promo_text": "🔥 Самая популярная беговая точка города!"
    },
    {
        "id": "promo_2",
        "title": "🚴 Велосипедные тренировки в Крылатском",
        "description": "Идеальные трассы для велотренировок",
        "lat": 55.756,
        "lng": 37.438,
        "sport": "велоспорт",
        "promo_text": "🏆 Профессиональные трассы для велоспорта"
    }
]


@app.route('/')
def root():
    return jsonify({"message": "SportEvents API is running", "status": "success"})


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


@app.route('/api/trainings', methods=['GET'])
def get_trainings():
    """Получить тренировки поблизости"""
    try:
        lat = request.args.get('lat', type=float)
        lng = request.args.get('lng', type=float)
        radius = request.args.get('radius', default=5, type=int)
        sport = request.args.get('sport', '')

        # Очистка старых тренировок (старше 24 часов)
        cleanup_old_trainings()

        nearby_trainings = []

        for training_id, training_data in trainings_storage.items():
            # Фильтр по виду спорта
            if sport and training_data.get('sport') != sport:
                continue

            # Фильтр по расстоянию
            if lat and lng:
                distance = calculate_distance(lat, lng, training_data["lat"], training_data["lng"])
                if distance <= radius:
                    training_data = training_data.copy()
                    training_data['distance'] = round(distance, 2)
                    training_data['participants_count'] = len(training_participants.get(training_id, []))
                    nearby_trainings.append(training_data)

        return jsonify({"status": "success", "data": nearby_trainings})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/trainings', methods=['POST'])
def create_training():
    """Создать новую тренировку"""
    try:
        data = request.get_json()
        print("Received training data:", data)

        # Валидация данных
        required_fields = ['user_id', 'title', 'sport', 'lat', 'lng', 'start_time']
        for field in required_fields:
            if not data.get(field):
                return jsonify({"status": "error", "message": f"Missing required field: {field}"}), 400

        training_id = f"training_{int(datetime.now().timestamp())}"

        training_data = {
            "id": training_id,
            "user_id": data['user_id'],
            "title": data['title'],
            "description": data.get('description', ''),
            "sport": data['sport'],
            "lat": float(data['lat']),
            "lng": float(data['lng']),
            "start_time": data['start_time'],
            "end_time": data.get('end_time'),
            "comment": data.get('comment', ''),
            "auto_accept": data.get('auto_accept', True),
            "created_at": datetime.now().isoformat(),
            "user_name": data['user_name'],
            "user_photo": data.get('user_photo')
        }

        trainings_storage[training_id] = training_data
        training_participants[training_id] = []

        # Автоматически добавляем создателя как участника
        join_training(training_id, data['user_id'], data['user_name'], data.get('user_photo'))

        logger.info(f"Training created successfully: {training_id}")

        return jsonify({
            "status": "success",
            "training_id": training_id,
            "message": "Training created successfully",
            "data": training_data
        })

    except Exception as e:
        logger.error(f"Error creating training: {str(e)}")
        return jsonify({"status": "error", "message": f"Server error: {str(e)}"}), 500


@app.route('/api/trainings/<training_id>/join', methods=['POST'])
def join_training_endpoint(training_id):
    """Присоединиться к тренировке"""
    try:
        data = request.get_json()

        if training_id not in trainings_storage:
            return jsonify({"status": "error", "message": "Тренировка не найдена"}), 404

        training = trainings_storage[training_id]

        # Проверка авто-принятия
        if training['auto_accept']:
            join_training(training_id, data['user_id'], data['user_name'], data.get('user_photo'))
            return jsonify({"status": "success", "message": "Вы присоединились к тренировке"})
        else:
            return jsonify({"status": "success", "message": "Запрос на участие отправлен организатору"})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


def join_training(training_id, user_id, user_name, user_photo):
    """Вспомогательная функция для присоединения к тренировке"""
    if training_id not in training_participants:
        training_participants[training_id] = []

    # Проверяем, не является ли пользователь уже участником
    for participant in training_participants[training_id]:
        if participant['user_id'] == user_id:
            return

    training_participants[training_id].append({
        "user_id": user_id,
        "user_name": user_name,
        "user_photo": user_photo,
        "joined_at": datetime.now().isoformat()
    })


@app.route('/api/trainings/<training_id>/participants', methods=['GET'])
def get_training_participants(training_id):
    """Получить список участников тренировки"""
    try:
        participants = training_participants.get(training_id, [])
        return jsonify({"status": "success", "data": participants})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/users/location', methods=['POST'])
def update_user_location():
    """Обновить местоположение пользователя"""
    try:
        data = request.get_json()

        user_locations[data['user_id']] = {
            "user_id": data['user_id'],
            "lat": data['lat'],
            "lng": data['lng'],
            "last_updated": datetime.now()
        }

        return jsonify({"status": "success", "message": "Location updated"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/promoted-locations', methods=['GET'])
def get_promoted_locations():
    """Получить рекламные локации"""
    return jsonify({"status": "success", "data": PROMOTED_LOCATIONS})


@app.route('/api/debug/trainings', methods=['GET'])
def debug_trainings():
    """Отладочный endpoint для просмотра всех тренировок"""
    return jsonify({
        "status": "success",
        "trainings_count": len(trainings_storage),
        "trainings": trainings_storage,
        "participants": training_participants
    })


def cleanup_old_trainings():
    """Очистка тренировок старше 24 часов"""
    current_time = datetime.now()
    training_ids_to_remove = []

    for training_id, training_data in trainings_storage.items():
        created_at = datetime.fromisoformat(training_data['created_at'])
        if current_time - created_at > timedelta(hours=24):
            training_ids_to_remove.append(training_id)

    for training_id in training_ids_to_remove:
        trainings_storage.pop(training_id, None)
        training_participants.pop(training_id, None)


def calculate_distance(lat1, lon1, lat2, lon2):
    """Расчет расстояния между точками (в км)"""
    return ((lat1 - lat2) ** 2 + (lon1 - lon2) ** 2) ** 0.5 * 111


if __name__ == "__main__":
    app.run(debug=True)