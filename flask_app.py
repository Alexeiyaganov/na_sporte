# flask_app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta
import logging
import json
import os

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Файлы для хранения данных
TRAININGS_FILE = 'trainings.json'
PARTICIPANTS_FILE = 'participants.json'

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

# Премиум тренировка (только одна)
PREMIUM_TRAINING = {
    "id": "premium_1",
    "title": "🔥 Премиум: Беговой клуб в Парке Горького",
    "description": "Элитная беговая группа с профессиональным тренером",
    "sport": "бег",
    "lat": 55.731,
    "lng": 37.603,
    "start_time": (datetime.now() + timedelta(days=1)).isoformat(),
    "end_time": (datetime.now() + timedelta(days=1, hours=2)).isoformat(),
    "comment": "Присоединяйтесь к нашей премиум группе! Профессиональный тренер, индивидуальный подход.",
    "auto_accept": True,
    "created_at": datetime.now().isoformat(),
    "user_name": "Профессиональный тренер",
    "user_photo": None,
    "is_premium": True,
    "participants_count": 12
}


def load_data():
    """Загрузка данных из файлов"""
    global trainings_storage, training_participants

    try:
        # Загрузка тренировок
        if os.path.exists(TRAININGS_FILE):
            with open(TRAININGS_FILE, 'r', encoding='utf-8') as f:
                trainings_storage = json.load(f)

        # Загрузка участников
        if os.path.exists(PARTICIPANTS_FILE):
            with open(PARTICIPANTS_FILE, 'r', encoding='utf-8') as f:
                training_participants = json.load(f)

        logger.info("Data loaded successfully")

    except Exception as e:
        logger.error(f"Error loading data: {str(e)}")
        trainings_storage = {}
        training_participants = {}


def save_data():
    """Сохранение данных в файлы"""
    try:
        # Сохранение тренировок
        with open(TRAININGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(trainings_storage, f, ensure_ascii=False, indent=2)

        # Сохранение участников
        with open(PARTICIPANTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(training_participants, f, ensure_ascii=False, indent=2)

        logger.info("Data saved successfully")

    except Exception as e:
        logger.error(f"Error saving data: {str(e)}")


def cleanup_old_trainings():
    """Очистка тренировок старше 1 дня после окончания"""
    current_time = datetime.now()
    training_ids_to_remove = []

    for training_id, training_data in trainings_storage.items():
        # Пропускаем премиум тренировки
        if training_data.get('is_premium'):
            continue

        end_time_str = training_data.get('end_time') or training_data.get('start_time')
        if end_time_str:
            try:
                end_time = datetime.fromisoformat(end_time_str.replace('Z', '+00:00'))
                # Удаляем если прошло более 1 дня после окончания
                if current_time - end_time > timedelta(days=1):
                    training_ids_to_remove.append(training_id)
            except ValueError as e:
                logger.warning(f"Invalid date format for training {training_id}: {e}")
                # Если дата некорректна, удаляем если создана более 2 дней назад
                created_at = datetime.fromisoformat(training_data['created_at'].replace('Z', '+00:00'))
                if current_time - created_at > timedelta(days=2):
                    training_ids_to_remove.append(training_id)

    for training_id in training_ids_to_remove:
        trainings_storage.pop(training_id, None)
        training_participants.pop(training_id, None)
        logger.info(f"Removed old training: {training_id}")

    if training_ids_to_remove:
        save_data()


# Загружаем данные при старте
load_data()

# Добавляем премиум тренировку если её нет
if 'premium_1' not in trainings_storage:
    trainings_storage['premium_1'] = PREMIUM_TRAINING
    training_participants['premium_1'] = []
    save_data()


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

        # Очистка старых тренировок
        cleanup_old_trainings()

        nearby_trainings = []

        for training_id, training_data in trainings_storage.items():
            # Фильтр по виду спорта
            if sport and training_data.get('sport') != sport:
                continue

            # Для премиум тренировок не применяем фильтр по расстоянию
            if training_data.get('is_premium'):
                training_data_copy = training_data.copy()
                training_data_copy['distance'] = 0
                training_data_copy['participants_count'] = len(training_participants.get(training_id, []))
                nearby_trainings.append(training_data_copy)
                continue

            # Фильтр по расстоянию для обычных тренировок
            if lat and lng:
                distance = calculate_distance(lat, lng, training_data["lat"], training_data["lng"])
                if distance <= radius:
                    training_data_copy = training_data.copy()
                    training_data_copy['distance'] = round(distance, 2)
                    training_data_copy['participants_count'] = len(training_participants.get(training_id, []))
                    nearby_trainings.append(training_data_copy)

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
            "user_photo": data.get('user_photo'),
            "is_premium": False
        }

        trainings_storage[training_id] = training_data
        training_participants[training_id] = []

        # Автоматически добавляем создателя как участника
        join_training(training_id, data['user_id'], data['user_name'], data.get('user_photo'))

        # Сохраняем данные
        save_data()

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
            save_data()  # Сохраняем после добавления участника
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


@app.route('/api/premium-training', methods=['GET'])
def get_premium_training():
    """Получить премиум тренировку"""
    return jsonify({"status": "success", "data": PREMIUM_TRAINING})


@app.route('/api/debug/trainings', methods=['GET'])
def debug_trainings():
    """Отладочный endpoint для просмотра всех тренировок"""
    return jsonify({
        "status": "success",
        "trainings_count": len(trainings_storage),
        "trainings": trainings_storage,
        "participants": training_participants
    })


def calculate_distance(lat1, lon1, lat2, lon2):
    """Расчет расстояния между точками (в км)"""
    return ((lat1 - lat2) ** 2 + (lon1 - lon2) ** 2) ** 0.5 * 111


if __name__ == "__main__":
    app.run(debug=True)