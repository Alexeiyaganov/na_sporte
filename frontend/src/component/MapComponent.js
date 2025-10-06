// frontend/src/components/MapComponent.js
import { onMounted, ref, watch, nextTick } from 'vue'
import { useStore } from '../store.js'

export default {
    props: {
        mode: {
            type: String,
            default: 'events'
        }
    },
    setup(props) {
        const store = useStore()
        const map = ref(null)
        const mapContainer = ref(null)
        const markers = ref(new Map())

        // Инициализация карты
        const initMap = async () => {
            await nextTick()

            if (!mapContainer.value) {
                console.error('Map container not found')
                return
            }

            try {
                map.value = L.map(mapContainer.value).setView([55.7558, 37.6173], 10)

                L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                    attribution: '© OpenStreetMap contributors'
                }).addTo(map.value)

                console.log('Map initialized successfully')
                updateMapMarkers()
            } catch (error) {
                console.error('Error initializing map:', error)
            }
        }

        // Обновление маркеров
        const updateMapMarkers = () => {
            if (!map.value) {
                console.log('Map not ready yet')
                return
            }

            // Очищаем старые маркеры
            markers.value.forEach(marker => {
                map.value.removeLayer(marker)
            })
            markers.value.clear()

            if (props.mode === 'events') {
                // Добавляем маркеры мероприятий
                store.filteredEvents.forEach(event => {
                    try {
                        const marker = L.marker([event.lat, event.lng])
                            .addTo(map.value)
                            .bindPopup(`
                                <div class="event-popup">
                                    <h4>${event.title}</h4>
                                    <p>${event.description}</p>
                                    <p><strong>Спорт:</strong> ${event.sport}</p>
                                    <p><strong>Дата:</strong> ${event.date}</p>
                                    <button onclick="window.app._instance.proxy.joinEvent(${event.id})">
                                        Участвовать
                                    </button>
                                </div>
                            `)

                        markers.value.set(`event_${event.id}`, marker)
                    } catch (error) {
                        console.error('Error creating event marker:', error)
                    }
                })

                console.log(`Added ${store.filteredEvents.length} event markers`)
            } else {
                // Режим "Люди рядом" - можно добавить позже
                console.log('People mode - no markers yet')
            }

            // Центрируем карту на пользователе если доступно
            if (store.state.userLocation) {
                map.value.setView(
                    [store.state.userLocation.lat, store.state.userLocation.lng],
                    12
                )
            }
        }

        onMounted(() => {
            console.log('MapComponent mounted')
            initMap()
        })

        watch(() => props.mode, updateMapMarkers)
        watch(() => store.filteredEvents, updateMapMarkers)
        watch(() => store.state.userLocation, (newLocation) => {
            if (newLocation && map.value) {
                map.value.setView([newLocation.lat, newLocation.lng], 12)
            }
        })

        return {
            mapContainer
        }
    },
    template: `
        <div ref="mapContainer" class="map-container"></div>
    `
}