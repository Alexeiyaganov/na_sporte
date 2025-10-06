// frontend/src/components/FilterPanel.js
import { useStore } from '../store.js'

export default {
    name: 'FilterPanel',
    setup() {
        const store = useStore()

        const sports = [
            { value: '', label: 'Все виды' },
            { value: 'бег', label: '🏃 Бег' },
            { value: 'велоспорт', label: '🚴 Велоспорт' },
            { value: 'лыжи', label: '⛷️ Лыжи' },
            { value: 'йога', label: '🧘 Йога' },
            { value: 'плавание', label: '🏊 Плавание' }
        ]

        const radii = [
            { value: 5, label: '5 км' },
            { value: 10, label: '10 км' },
            { value: 25, label: '25 км' },
            { value: 50, label: '50 км' }
        ]

        const shareLocation = async () => {
            try {
                const location = await store.requestLocation()
                await store.updateUserLocation(location.lat, location.lng, 'Ищу мероприятия рядом')
                alert('Геолокация обновлена! Карта отцентрирована на вашем местоположении.')
            } catch (error) {
                console.error('Error getting location:', error)
                alert('Не удалось получить геолокацию. Проверьте разрешения в браузере.')
            }
        }

        return {
            store,
            sports,
            radii,
            shareLocation
        }
    },
    template: `
        <div class="filters-panel">
            <select 
                v-model="store.state.filters.sport" 
                class="filter-select"
            >
                <option 
                    v-for="sport in sports" 
                    :key="sport.value" 
                    :value="sport.value"
                >
                    {{ sport.label }}
                </option>
            </select>
            
            <select 
                v-model="store.state.filters.radius" 
                class="filter-select"
                :disabled="!store.state.userLocation"
            >
                <option 
                    v-for="radius in radii" 
                    :key="radius.value" 
                    :value="radius.value"
                >
                    {{ radius.label }}
                </option>
            </select>
            
            <button 
                @click="shareLocation" 
                class="location-btn"
                :title="store.state.userLocation ? 'Обновить геолокацию' : 'Поделиться геолокацией'"
            >
                📍 {{ store.state.userLocation ? 'Обновить' : 'Мое местоположение' }}
            </button>
            
            <span v-if="store.state.isLoading" style="color: #666;">
                Загрузка мероприятий...
            </span>
        </div>
    `
}