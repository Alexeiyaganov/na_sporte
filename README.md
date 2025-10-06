sport-events-app/
├── frontend/
│   └── index.html              # Vue.js приложение
├── backend/
│   ├── events-service/
│   │   ├── main.py
│   │   └── requirements.txt
│   └── users-service/
│       ├── main.py
│       └── requirements.txt
├── telegram-bot/
│   ├── bot.py
│   └── requirements.txt
└── README.md


# 🏃 SportEvents Map

Telegram Mini App для поиска спортивных мероприятий и напарников.

## 🚀 Быстрый старт

### 1. Запуск бэкенда
```bash
# Terminal 1 - Events Service
cd backend/events-service
pip install -r requirements.txt
python main.py

# Terminal 2 - Users Service  
cd backend/users-service
pip install -r requirements.txt
python main.py
2. Запуск фронтенда
bash
cd frontend
python -m http.server 8080
3. Запуск бота
bash
cd telegram-bot
pip install -r requirements.txt
python bot.py