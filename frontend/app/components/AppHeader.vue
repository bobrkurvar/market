<template>
  <header class="sticky top-0 z-50 backdrop-blur-md bg-slate-950/70 border-b border-gray-100/10">
    <UContainer class="flex items-center justify-between h-16 gap-4">

      <div
        class="text-xl font-black tracking-wider text-primary-500 cursor-pointer flex items-center gap-1 flex-shrink-0 outline-none"
        @click="goHome"
      >
        my<span class="text-white">Market</span>
      </div>

      <div class="relative flex-1 max-w-2xl hidden md:block">
        <UInput
          v-model="searchInput"
          icon="i-heroicons-magnifying-glass"
          placeholder="Найти игру, подписку, аккаунт или ключ..."
          size="md"
          :ui="{ icon: { trailing: { pointer: '' } } }"
          @keyup.enter="applySearch"
          @blur="handleBlur"
          autocomplete="off"
          class="w-full shadow-sm"
        >
          <template #trailing>
            <UButton
              v-show="searchInput !== ''"
              color="gray"
              variant="link"
              icon="i-heroicons-x-mark"
              :padded="false"
              @click="clearSearch"
            />
          </template>
        </UInput>

        <div
          v-if="suggestions.length > 0"
          class="absolute w-full mt-1 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-md shadow-lg z-50 overflow-hidden text-gray-900 dark:text-white"
        >
          <ul class="max-h-60 overflow-y-auto">
            <li
              v-for="item in suggestions"
              :key="(item.data && item.data.id) ? item.data.id : item.name"
              @mousedown="selectSuggestion(item)"
              class="px-4 py-3 hover:bg-gray-100 dark:hover:bg-gray-800 cursor-pointer flex justify-between items-center transition-colors"
            >
              <div class="flex items-center gap-2">
                <img v-if="item.data && item.data.search_url" :src="item.data.search_url" :alt="item.data.name" class="w-5 h-5 object-contain" />
                <UIcon v-else name="i-heroicons-folder" class="text-gray-400 w-5 h-5" />
                <span class="font-medium">{{ item.data ? item.data.name : item.name }}</span>
              </div>
              <span v-if="item.match_count" class="text-xs text-gray-500 bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded-full">
                {{ item.match_count }}
              </span>
            </li>
          </ul>
        </div>
      </div>

      <div class="flex items-center gap-3 flex-shrink-0">
        <UButton
          :icon="colorMode.value === 'dark' ? 'i-heroicons-sun-20-solid' : 'i-heroicons-moon-20-solid'"
          color="neutral"
          variant="ghost"
          aria-label="Theme"
          @click="colorMode.preference = colorMode.value === 'dark' ? 'light' : 'dark'"
        />

        <UButton v-if="!currentUser" to="/login" color="neutral" variant="subtle" class="font-medium px-4">
          Войти
        </UButton>

        <UDropdownMenu v-else :items="dropdownItems">
          <UButton color="neutral" variant="ghost" class="text-gray-200 hover:bg-slate-900" trailing-icon="i-heroicons-chevron-down-20-solid">
            <UAvatar :alt="currentUser.username" size="xs" class="mr-1 bg-primary-500 text-white font-bold" />
            {{ currentUser.username }}
            <span class="text-xs text-gray-400 ml-1">({{ currentUser.role === 'seller' ? 'Продавец' : 'Клиент' }})</span>
          </UButton>
        </UDropdownMenu>
      </div>

    </UContainer>
  </header>
</template>

<script setup>
import { ref, watch, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const currentUser = useState('user')
const colorMode = useColorMode()
const { $api } = useNuxtApp()

// --- МЕНЮ ПРОФИЛЯ ---
const dropdownItems = [
  [{
    label: 'Панель управления',
    icon: 'i-heroicons-cog-8-tooth',
    onSelect: () => {
       const path = currentUser.value.role === 'seller' ? '/seller' : '/profile'
       router.push(path)
    }
  }],
  [{
    label: 'Выйти',
    icon: 'i-heroicons-arrow-right-on-rectangle',
    onSelect: async () => {
      try {
        await $api('/api/logout', { method: 'POST' })
      } catch (e) {}
      currentUser.value = null
      router.push('/')
    }
  }]
]

// --- ЛОГИКА ПОИСКА ---
const searchInput = ref(route.query.q || '')
const suggestions = ref([])
let ws = null
let idleTimeout = null
const IDLE_TIME_MS = 30000

const goHome = () => {
  clearSearch()
}

const applySearch = () => {
  suggestions.value = []
  closeWebSocket()
  router.push({
    path: '/',
    query: { q: searchInput.value || undefined }
  })
}

const clearSearch = () => {
  searchInput.value = ''
  suggestions.value = []
  closeWebSocket()
  router.push({ path: '/' })
}

const selectSuggestion = (item) => {
  suggestions.value = []
  closeWebSocket()

  // Если прилетел ожидаемый "конверт"
  if (item && item.data) {
    const targetData = item.data
    const targetId = targetData.id || targetData.category_id

    // Если это категория и у нас есть все нужные данные
    if (item.type === 'category' && targetId && targetData.slug) {
      searchInput.value = ''
      router.push(`/categories/${targetData.slug}/${targetId}`)
      return
    }

    // Если это продукт (на будущее)
    if (item.type === 'product' && targetId && targetData.slug) {
       searchInput.value = ''
       router.push(`/products/${targetData.slug}/${targetId}`)
       return
    }

    // Фолбэк для текстового поиска, если что-то пошло не так
    searchInput.value = targetData.name || searchInput.value
    applySearch()
  } else {
    // Страховка на случай старого формата данных
    searchInput.value = item.name || searchInput.value
    applySearch()
  }
}

// --- WEBSOCKETS (ПОДСКАЗКИ) ---
const resetIdleTimeout = () => {
  if (idleTimeout) clearTimeout(idleTimeout)
  idleTimeout = setTimeout(() => {
    closeWebSocket()
  }, IDLE_TIME_MS)
}

const closeWebSocket = () => {
  if (ws && (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING)) {
    ws.close()
    ws = null
  }
  if (idleTimeout) clearTimeout(idleTimeout)
}

const connectWebSocket = () => {
  if (ws && (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING)) {
    return
  }

  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const wsUrl = `${protocol}//${window.location.host}/api/ws/search`;
  ws = new WebSocket(wsUrl)

  ws.onopen = () => {
    if (searchInput.value.length >= 3) {
      ws.send(searchInput.value)
    }
    resetIdleTimeout()
  }

  ws.onmessage = (event) => {
    const data = JSON.parse(event.data)
    suggestions.value = data.suggestions || []
    resetIdleTimeout()
  }
}

const handleBlur = () => {
  setTimeout(() => {
    suggestions.value = []
    closeWebSocket()
  }, 200)
}

watch(searchInput, (newVal) => {
  if (newVal.length >= 3) {
    if (!ws || ws.readyState === WebSocket.CLOSED) {
      connectWebSocket()
    } else if (ws.readyState === WebSocket.OPEN) {
      ws.send(newVal)
      resetIdleTimeout()
    }
  } else {
    suggestions.value = []
    if (newVal.length === 0) {
      closeWebSocket()
    }
  }
})

watch(() => route.query.q, (newQ) => {
  if (searchInput.value !== newQ) {
    searchInput.value = newQ || ''
  }
})

onUnmounted(() => {
  closeWebSocket()
})
</script>
