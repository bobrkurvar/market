<template>
  <header class="sticky top-0 z-50 border-b border-gray-200/70 bg-white/85 backdrop-blur-xl dark:border-gray-800 dark:bg-gray-950/80">
    <UContainer class="py-3">
      <div class="flex items-center justify-between gap-4">
        <button
          type="button"
          class="group flex flex-shrink-0 items-center gap-2 rounded-2xl outline-none transition-transform hover:scale-[1.02]"
          @click="goHome"
        >
          <span class="flex h-10 w-10 items-center justify-center rounded-2xl bg-primary-500 text-white shadow-lg shadow-primary-500/20">
            <UIcon name="i-heroicons-shopping-bag" class="h-6 w-6" />
          </span>
          <span class="text-xl font-black tracking-tight text-gray-950 dark:text-white">
            my<span class="text-primary-500">Market</span>
          </span>
        </button>

        <div class="relative hidden max-w-2xl flex-1 md:block">
          <UInput
            v-model="searchInput"
            icon="i-heroicons-magnifying-glass"
            placeholder="Найти игру, подписку, аккаунт или ключ..."
            size="lg"
            :ui="{ icon: { trailing: { pointer: '' } } }"
            autocomplete="off"
            class="w-full"
            @keyup.enter="applySearch"
            @blur="handleBlur"
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
            class="absolute z-50 mt-2 w-full overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-2xl dark:border-gray-800 dark:bg-gray-900"
          >
            <div class="border-b border-gray-100 px-4 py-3 text-xs font-semibold uppercase tracking-[0.16em] text-gray-400 dark:border-gray-800">
              Быстрые подсказки
            </div>
            <ul class="max-h-80 overflow-y-auto p-2">
              <li
                v-for="item in suggestions"
                :key="(item.data && item.data.id) ? item.data.id : item.name"
                class="flex cursor-pointer items-center justify-between rounded-xl px-3 py-3 transition-colors hover:bg-gray-50 dark:hover:bg-gray-800"
                @mousedown="selectSuggestion(item)"
              >
                <div class="flex min-w-0 items-center gap-3">
                  <span class="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-xl bg-gray-100 dark:bg-gray-800">
                    <img v-if="item.data && item.data.search_url" :src="item.data.search_url" :alt="item.data.name" class="h-6 w-6 object-contain" />
                    <UIcon v-else name="i-heroicons-folder" class="h-5 w-5 text-gray-400" />
                  </span>
                  <div class="min-w-0">
                    <div class="truncate font-semibold text-gray-950 dark:text-white">{{ item.data ? item.data.name : item.name }}</div>
                    <div class="text-xs text-gray-500">{{ item.type === 'category' ? 'Категория' : 'Товар' }}</div>
                  </div>
                </div>
                <span v-if="item.match_count" class="rounded-full bg-primary-50 px-2.5 py-1 text-xs font-bold text-primary-500 dark:bg-primary-950/40">
                  {{ item.match_count }}
                </span>
              </li>
            </ul>
          </div>
        </div>

        <div class="flex flex-shrink-0 items-center gap-2 sm:gap-3">
          <UButton
            :icon="colorMode.value === 'dark' ? 'i-heroicons-sun-20-solid' : 'i-heroicons-moon-20-solid'"
            color="gray"
            variant="soft"
            aria-label="Theme"
            class="rounded-xl"
            @click="colorMode.preference = colorMode.value === 'dark' ? 'light' : 'dark'"
          />

          <UButton v-if="!currentUser" to="/login" color="primary" variant="soft" class="rounded-xl px-4 font-semibold">
            Войти
          </UButton>

          <UDropdownMenu v-else :items="dropdownItems">
            <UButton color="gray" variant="soft" class="rounded-xl font-semibold" trailing-icon="i-heroicons-chevron-down-20-solid">
              <UAvatar :alt="currentUser.username" size="xs" class="mr-1 bg-primary-500 text-white font-bold" />
              <span class="hidden sm:inline">{{ currentUser.username }}</span>
              <span class="hidden text-xs text-gray-400 lg:inline">{{ currentUser.role === 'seller' ? 'Продавец' : 'Клиент' }}</span>
            </UButton>
          </UDropdownMenu>
        </div>
      </div>

      <div class="relative mt-3 md:hidden">
        <UInput
          v-model="searchInput"
          icon="i-heroicons-magnifying-glass"
          placeholder="Найти товар..."
          size="lg"
          autocomplete="off"
          @keyup.enter="applySearch"
          @blur="handleBlur"
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
          class="absolute z-50 mt-2 w-full overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-2xl dark:border-gray-800 dark:bg-gray-900"
        >
          <ul class="max-h-72 overflow-y-auto p-2">
            <li
              v-for="item in suggestions"
              :key="(item.data && item.data.id) ? item.data.id : item.name"
              class="flex cursor-pointer items-center gap-3 rounded-xl px-3 py-3 transition-colors hover:bg-gray-50 dark:hover:bg-gray-800"
              @mousedown="selectSuggestion(item)"
            >
              <span class="flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-xl bg-gray-100 dark:bg-gray-800">
                <img v-if="item.data && item.data.search_url" :src="item.data.search_url" :alt="item.data.name" class="h-5 w-5 object-contain" />
                <UIcon v-else name="i-heroicons-folder" class="h-5 w-5 text-gray-400" />
              </span>
              <span class="truncate font-semibold text-gray-950 dark:text-white">{{ item.data ? item.data.name : item.name }}</span>
            </li>
          </ul>
        </div>
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

  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  const wsUrl = `${protocol}//${window.location.host}/api/ws/search`
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
