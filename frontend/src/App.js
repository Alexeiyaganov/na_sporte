// frontend/src/App.js
import { createApp, ref, onMounted, computed } from 'vue'
import { useStore } from './store.js'
import MapComponent from './components/MapComponent.js'
import FilterPanel from './components/FilterPanel.js'
import UserProfile from './components/UserProfile.js'

const App = {
    name: 'App',
    components: {
        MapComponent,
        FilterPanel,
        UserProfile
    },
    setup() {
        const store = useStore()
        const activeTab = ref('events')

        onMounted(async () => {
            console.log('Initializing app...')
            await store.initTelegramApp()
            await store.loadEvents()
        })

        return {
            activeTab,
            store
        }
    },
    template: `
        <div class="app-container">
            <header class="app-header">
                <h1>🏃 SportEvents Map</h1>
            </header>
            
            <nav class="nav-tabs">
                <button 
                    @click="activeTab = 'events'" 
                    :class="{ active: activeTab === 'events' }"
                    class="tab-button"
                >
                    🗓️ Мероприятия
                </button>
                <button 
                    @click="activeTab = 'people'" 
                    :class="{ active: activeTab === 'people' }"
                    class="tab-button"
                >
                    👥 Люди рядом
                </button>
            </nav>
            
            <FilterPanel v-if="activeTab === 'events'" />
            <UserProfile v-if="activeTab === 'people'" />
            
            <MapComponent :mode="activeTab" />
        </div>
    `
}

// Создаем и монтируем приложение
const app = createApp(App)
app.mount('#app')

// Делаем app глобально доступной для обработчиков событий в popup
window.app = app