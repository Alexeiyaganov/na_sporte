// frontend/src/store.js
import { reactive, computed } from 'vue'

class AppStore {
    constructor() {
        this.state = reactive({
            events: [],
            users: [],
            filters: {
                sport: '',
                radius: 10,
                search: ''
            },
            userLocation: null,
            userProfile: null,
            telegramApp: null,
            isLoading: false
        })
    }

    // Инициализация Telegram WebApp
    async initTelegramApp() {
        // Для разработки без Telegram - создаем mock
        if (window.Telegram && window.Telegram.WebApp) {
            this.state.telegramApp = Telegram.WebApp
            this.state.telegramApp.ready()
            this.state.telegramApp.expand()
            this.state.userProfile = this.state.telegramApp.initDataUnsafe.user
        } else {
            console.log('Running in development mode (no Telegram WebApp)')
            this.state.userProfile = {
                id: 123456789,
                first_name: 'Demo',
                username: 'demo_user'
            }
        }
    }

    // Загрузка мероприятий
    async loadEvents() {
        this.state.isLoading = true
        try {
            const response = await fetch('http://localhost:8001/api/events')
            if (!response.ok) throw new Error('Network response was not ok')
            this.state.events = await response.json()
            console.log('Loaded events:', this.state.events.length)
        } catch (error) {
            console.error('Failed to load events:', error)
            // Fallback to mock data
            this.state.events = this.getMockEvents()
        } finally {
            this.state.isLoading = false
        }
    }

    // Фильтрованные мероприятия
    get filteredEvents() {
        let events = this.state.events

        if (this.state.filters.sport) {
            events = events.filter(event =>
                event.sport === this.state.filters.sport
            )
        }

        if (this.state.userLocation && this.state.filters.radius) {
            events = events.filter(event => {
                const distance = this.calculateDistance(
                    this.state.userLocation.lat,
                    this.state.userLocation.lng,
                    event.lat,
                    event.lng
                )
                return distance <= this.state.filters.radius
            })
        }

        return events
    }

    // Обновление геолокации
    async updateUserLocation(lat, lng, comment = '') {
        this.state.userLocation = { lat, lng }
        console.log('User location updated:', { lat, lng, comment })

        try {
            const response = await fetch('http://localhost:8002/api/users/location', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify({
                    user_id: this.state.userProfile?.id,
                    username: this.state.userProfile?.username || this.state.userProfile?.first_name,
                    lat: lat,
                    lng: lng,
                    comment: comment
                })
            })

            if (!response.ok) throw new Error('Failed to update location')

            const result = await response.json()
            console.log('Location saved to server:', result)
        } catch (error) {
            console.error('Failed to update location on server:', error)
        }
    }

    // Запрос геолокации у пользователя
    async requestLocation() {
        return new Promise((resolve, reject) => {
            if (!navigator.geolocation) {
                reject(new Error('Geolocation is not supported'))
                return
            }

            navigator.geolocation.getCurrentPosition(
                (position) => {
                    const location = {
                        lat: position.coords.latitude,
                        lng: position.coords.longitude
                    }
                    resolve(location)
                },
                (error) => {
                    reject(error)
                },
                {
                    enableHighAccuracy: true,
                    timeout: 10000,
                    maximumAge: 60000
                }
            )
        })
    }

    // Вспомогательная функция расчета расстояния
    calculateDistance(lat1, lon1, lat2, lon2) {
        const R = 6371 // Earth radius in km
        const dLat = (lat2 - lat1) * Math.PI / 180
        const dLon = (lon2 - lon1) * Math.PI / 180
        const a =
            Math.sin(dLat/2) * Math.sin(dLat/2) +
            Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
            Math.sin(dLon/2) * Math.sin(dLon/2)
        const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a))
        return R * c
    }

    // Mock данные для разработки
    getMockEvents() {
        return [
            {
                id: 1,
                title: "Московский марафон 2024",
                description: "Ежегодный осенний марафон через центр Москвы",
                sport: "бег",
                date: "2024-09-15",
                location: "Москва, Воробьевы горы",
                lat: 55.710,
                lng: 37.553
            },
            {
                id: 2,
                title: "Ночной велопробег",
                description: "Ночная велопрогулка по освещенным улицам города",
                sport: "велоспорт",
                date: "2024-10-20",
                location: "Москва, Парк Горького",
                lat: 55.731,
                lng: 37.603
            },
            {
                id: 3,
                title: "Открытие лыжного сезона",
                description: "Групповая лыжная прогулка в Крылатском",
                sport: "лыжи",
                date: "2024-12-10",
                location: "Москва, Крылатское",
                lat: 55.756,
                lng: 37.438
            },
            {
                id: 4,
                title: "Йога в парке",
                description: "Бесплатное занятие йогой на свежем воздухе",
                sport: "йога",
                date: "2024-08-25",
                location: "Москва, Сокольники",
                lat: 55.795,
                lng: 37.679
            }
        ]
    }

    // Глобальные методы для popup
    joinEvent(eventId) {
        console.log('Joining event:', eventId)
        alert(`Вы присоединились к мероприятию ${eventId}`)
    }

    requestContact(userId) {
        console.log('Requesting contact with user:', userId)
        alert(`Запрос на контакт отправлен пользователю ${userId}`)
    }
}

const store = new AppStore()

export function useStore() {
    return store
}

export default store