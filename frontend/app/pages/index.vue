<template>
  <UContainer class="py-6 min-h-screen flex flex-col">

    <div class="w-full mb-8 relative z-50">
      <div class="flex items-center gap-4">
        <NuxtLink to="/" class="hidden md:block outline-none" @click="clearSearch">
          <h2 class="text-2xl font-extrabold text-primary-500 tracking-tight cursor-pointer">
            myMarket
          </h2>
        </NuxtLink>

        <div class="relative flex-grow">
          <UInput
            v-model="searchInput"
            icon="i-heroicons-magnifying-glass"
            placeholder="Найти игру, подписку, аккаунт или ключ..."
            size="xl"
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
            class="absolute w-full mt-1 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-md shadow-lg z-50 overflow-hidden"
          >
            <ul class="max-h-60 overflow-y-auto">
              <li
                v-for="item in suggestions"
                :key="item.id"
                @click="selectSuggestion(item)"
                class="px-4 py-3 hover:bg-gray-100 dark:hover:bg-gray-800 cursor-pointer flex justify-between items-center transition-colors"
              >
                <div class="flex items-center gap-2">
                  <UIcon name="i-heroicons-folder" class="text-gray-400 w-5 h-5" />
                  <span class="font-medium">{{ item.name }}</span>
                </div>
                <span v-if="item.match_count" class="text-xs text-gray-500 bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded-full">
                  {{ item.match_count }}
                </span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>

    <div class="text-center space-y-4 mb-12 mt-4 transition-all" v-if="!route.query.q">
      <h1 class="text-4xl md:text-5xl font-extrabold tracking-tight sm:text-6xl">
        Твой Маркетплейс Цифровых Товаров
      </h1>
      <p class="text-lg opacity-80 max-w-2xl mx-auto">
        Лицензионные ключи, подписки, игровая валюта и аккаунты. Моментальная доставка на email сразу после оплаты.
      </p>
    </div>

    <div v-if="route.query.q" class="mb-6">
      <h2 class="text-2xl font-bold">
        Результаты по запросу: <span class="text-primary-500">«{{ route.query.q }}»</span>
      </h2>
    </div>

    <div v-if="pending" class="flex justify-center py-20">
      <UIcon name="i-heroicons-arrow-path" class="animate-spin w-10 h-10 text-primary-500" />
    </div>

    <div v-else-if="products.length > 0" class="flex-grow">
      <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6 mb-10">
        <NuxtLink
          v-for="product in products"
          :key="product.id"
          :to="`/products/${product.id}`"
          class="block outline-none"
        >
          <UCard
            class="flex flex-col h-full cursor-pointer transition-all duration-200 hover:ring-2 hover:ring-primary-500 hover:shadow-md overflow-hidden"
            :ui="{ header: { padding: 'p-0 sm:p-0' }, body: { padding: 'p-4 sm:p-4 flex-grow flex flex-col' } }"
          >
            <template #header>
              <div class="aspect-video w-full bg-gray-100 dark:bg-gray-800 flex items-center justify-center overflow-hidden relative">
                <img
                  v-if="product.thumbnail_url"
                  :src="product.thumbnail_url"
                  @error="$event.target.src = product.image_url"
                  :alt="product.title"
                  class="w-full h-full object-cover transition-transform duration-300 hover:scale-105"
                />
                <img
                  v-else-if="product.image_url"
                  :src="product.image_url"
                  :alt="product.title"
                  class="w-full h-full object-cover transition-transform duration-300 hover:scale-105"
                />
                <UIcon
                  v-else
                  name="i-heroicons-photo"
                  class="w-12 h-12 text-gray-300 dark:text-gray-600"
                />
              </div>
            </template>

            <div class="font-bold text-lg truncate" :title="product.title">{{ product.title }}</div>
            <p class="text-sm text-gray-600 dark:text-gray-300 line-clamp-2 mt-2 flex-grow">
              {{ product.description }}
            </p>

            <template #footer>
              <div class="flex items-center justify-between">
                <span class="text-xl font-bold text-green-600 dark:text-green-400">
                  {{ product.price }} ₽
                </span>
                <UButton color="primary" size="sm" icon="i-heroicons-shopping-cart" pointer-events-none>
                  Купить
                </UButton>
              </div>
            </template>
          </UCard>
        </NuxtLink>
      </div>

      <div class="flex justify-center mt-8" v-if="totalItems > itemsPerPage">
        <UPagination
          v-model="page"
          :total="totalItems"
          :page-count="itemsPerPage"
          :prev-button="{ icon: 'i-heroicons-arrow-small-left', color: 'gray', variant: 'outline' }"
          :next-button="{ icon: 'i-heroicons-arrow-small-right', color: 'gray', variant: 'outline' }"
        />
      </div>
    </div>

    <div v-else class="text-center py-20 flex-grow">
      <UIcon name="i-heroicons-face-frown" class="w-16 h-16 text-gray-400 mx-auto mb-4" />
      <h3 class="text-xl font-bold">Ничего не найдено</h3>
      <p class="text-gray-500 mt-2">Попробуйте изменить поисковой запрос</p>
      <UButton class="mt-4" color="primary" variant="soft" @click="clearSearch">
        Сбросить поиск
      </UButton>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-8 mt-auto border-t border-gray-200 dark:border-gray-800 pt-16 mb-10">
      <div class="text-center">
        <UIcon name="i-heroicons-bolt" class="w-10 h-10 text-primary-500 mx-auto mb-4" />
        <h3 class="text-xl font-bold mb-2">Моментальная выдача</h3>
        <p class="text-gray-500 text-sm">Ключ активации появляется на экране и дублируется на почту ровно через секунду после оплаты.</p>
      </div>
      <div class="text-center">
        <UIcon name="i-heroicons-shield-check" class="w-10 h-10 text-primary-500 mx-auto mb-4" />
        <h3 class="text-xl font-bold mb-2">Безопасная сделка</h3>
        <p class="text-gray-500 text-sm">Деньги переводятся продавцу только после того, как ты подтвердишь валидность ключа или аккаунта.</p>
      </div>
      <div class="text-center">
        <UIcon name="i-heroicons-users" class="w-10 h-10 text-primary-500 mx-auto mb-4" />
        <h3 class="text-xl font-bold mb-2">Сотни продавцов</h3>
        <p class="text-gray-500 text-sm">Конкуренция рождает лучшие цены. Выбирай товары по отзывам и рейтингу продавцов.</p>
      </div>
    </div>
  </UContainer>
</template>

<script setup>
import { computed, ref, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const { $api } = useNuxtApp()
const itemsPerPage = 8

// --- 1. Логика поиска (REST) ---
const searchInput = ref(route.query.q || '')

const applySearch = () => {
  suggestions.value = [] // Прячем выпадашку при полном поиске
  closeWebSocket()       // Закрываем сокет, так как поиск завершен
  router.push({
    query: {
      ...route.query,
      q: searchInput.value || undefined,
      page: 1
    }
  })
}

const clearSearch = () => {
  searchInput.value = ''
  suggestions.value = []
  closeWebSocket()       // Закрываем сокет при сбросе
  applySearch()
}

// --- 2. Логика WebSocket (Подсказки) ---
const suggestions = ref([])
let ws = null
let idleTimeout = null
const IDLE_TIME_MS = 30000 // Закрываем соединение после 30 секунд неактивности

// Сброс таймера простоя
const resetIdleTimeout = () => {
  if (idleTimeout) clearTimeout(idleTimeout)
  idleTimeout = setTimeout(() => {
    console.log('WS закрыт по таймауту бездействия')
    closeWebSocket()
  }, IDLE_TIME_MS)
}

const closeWebSocket = () => {
  if (ws && (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING)) {
    ws.close()
    ws = null
    console.log('WS принудительно закрыт')
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
    console.log('WS соединение установлено')
    // Если пока сокет открывался, пользователь уже ввел 3+ символа, отправляем запрос
    if (searchInput.value.length >= 3) {
      ws.send(searchInput.value)
    }
    resetIdleTimeout()
  }

  ws.onmessage = (event) => {
    const data = JSON.parse(event.data)
    suggestions.value = data.suggestions || []
    resetIdleTimeout() // Запрос успешен, обновляем таймер активности
  }

  ws.onerror = (error) => {
    console.error('WS Ошибка:', error)
  }
}

// Обработка потери фокуса (клик мимо инпута)
const handleBlur = () => {
  // Задержка нужна, чтобы клик по подсказке из выпадающего меню успел сработать
  setTimeout(() => {
    suggestions.value = []
    closeWebSocket()
  }, 200)
}

// Следим за вводом: открываем сокет, отправляем запросы, закрываем если стерли текст
watch(searchInput, (newVal) => {
  if (newVal.length >= 3) {
    if (!ws || ws.readyState === WebSocket.CLOSED) {
      // Соединения нет — открываем (отправка первого текста произойдет в onopen)
      connectWebSocket()
    } else if (ws.readyState === WebSocket.OPEN) {
      // Соединение есть — отправляем новый текст
      ws.send(newVal)
      resetIdleTimeout()
    }
  } else {
    suggestions.value = []
    // Если полностью очистили поле ввода, можно разорвать соединение
    if (newVal.length === 0) {
      closeWebSocket()
    }
  }
})

// Закрываем сокет, если уходим на другую страницу (unmount компонента)
onUnmounted(() => {
  closeWebSocket()
})

// Клик по подсказке
const selectSuggestion = (item) => {
  searchInput.value = item.name
  suggestions.value = []
  applySearch() // Запускает поиск и закрывает сокет внутри функции
}

// --- 3. Логика пагинации и загрузки данных ---
const page = computed({
  get: () => Number(route.query.page) || 1,
  set: (val) => {
    router.push({ query: { ...route.query, page: val } })
  }
})

const currentOffset = computed(() => (page.value - 1) * itemsPerPage)

const { data, pending, error } = await useFetch('/api/products', {
  $fetch: $api,
  query: {
    limit: itemsPerPage,
    offset: currentOffset,
    q: computed(() => route.query.q)
  },
  watch: [() => route.query.q]
})

const products = computed(() => data.value?.items || [])
const totalItems = computed(() => data.value?.total || 0)

useHead({
  title: 'Твой Маркетплейс Цифровых Товаров | myMarket'
})
</script>
