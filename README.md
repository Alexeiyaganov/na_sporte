┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Telegram      │    │    API Gateway   │    │   Frontend      │
│     Bot         │───▶│   (Nginx)        │───▶│  (Vue.js)       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
              ┌───────────────┼───────────────┐
              │               │               │
              ▼               ▼               ▼
    ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
    │   Events Service │ │   Users Service │ │   Auth Service  │
    │   (Python)       │ │   (Python)      │ │   (Python)      │
    └─────────────────┘ └─────────────────┘ └─────────────────┘
              │                   │
              ▼                   ▼
    ┌─────────────────┐ ┌─────────────────┐
    │   Redis Cache   │ │   PostgreSQL    │
    └─────────────────┘ └─────────────────┘
    
    
    2. Структура проекта
    
    na sporte/
├── frontend/                 # Vue.js приложение
│   ├── src/
│   │   ├── components/
│   │   ├── views/
│   │   ├── stores/
│   │   └── utils/
│   └── public/
├── backend/
│   ├── events-service/       # Сервис мероприятий
│   ├── users-service/        # Сервис пользователей
│   ├── shared/               # Общие утилиты
│   └── requirements.txt
├── nginx/                    # Конфигурация API Gateway
├── docker-compose.yml
└── README.md