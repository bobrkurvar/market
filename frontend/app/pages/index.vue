<template>
  <UContainer class="py-6 min-h-screen flex flex-col">

    <div v-if="!isSearchActive" class="flex-grow flex flex-col">
      <div class="text-center space-y-4 mb-12 mt-4 transition-all">
        <h1 class="text-4xl md:text-5xl font-extrabold tracking-tight sm:text-6xl">
          Твой Маркетплейс Цифровых Товаров
        </h1>
        <p class="text-lg opacity-80 max-w-2xl mx-auto">
          Лицензионные ключи, подписки, игровая валюта и аккаунты. Моментальная доставка на email сразу после оплаты.
        </p>
      </div>

      <div v-if="homePending" class="flex justify-center py-20">
        <UIcon name="i-heroicons-arrow-path" class="animate-spin w-10 h-10 text-primary-500" />
      </div>

      <template v-else>
        <div class="mb-12" v-if="popularCategories.length > 0">
          <h2 class="text-2xl font-bold mb-6">Популярные категории</h2>
          <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
            <UCard
              v-for="category in popularCategories"
              :key="category.id"
              class="cursor-pointer hover:ring-2 hover:ring-primary-500 hover:shadow-md transition-all flex items-center justify-center text-center h-20"
              :ui="{ body: { padding: 'p-2 sm:p-4' } }"
              @click="searchByCategory(category.name)"
            >
              <span class="font-semibold line-clamp-2">{{ category.name }}</span>
            </UCard>
          </div>
        </div>

        <div class="mb-12" v-if="popularProducts.length > 0">
          <h2 class="text-2xl font-bold mb-6">Хиты продаж</h2>
          <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
            <NuxtLink
              v-for="product in popularProducts"
              :key="product.id"
              :to="`/products/${product.slug}/${product.id}`"
              class="block outline-none"
            >
              <UCard
                class="flex flex-col h-full cursor-pointer transition-all duration-200 hover:ring-2 hover:ring-primary-500 hover:shadow-md overflow-hidden"
                :ui="{ header: { padding: 'p-0 sm:p-0' }, body: { padding: 'p-4 sm:p-4 flex-grow flex flex-col' } }"
              >
                <template #header>
                  <div class="aspect-video w-full bg-gray-100 dark:bg-gray-800 flex items-center justify-center overflow-hidden relative">
                    <img v-if="product.thumbnail_url" :src="product.thumbnail_url" @error="$event.target.src = product.image_url" :alt="product.title" class="w-full h-full object-cover transition-transform duration-300 hover:scale-105" />
                    <img v-else-if="product.image_url" :src="product.image_url" :alt="product.title" class="w-full h-full object-cover transition-transform duration-300 hover:scale-105" />
                    <UIcon v-else name="i-heroicons-photo" class="w-12 h-12 text-gray-300 dark:text-gray-600" />
                  </div>
                </template>
                <div class="font-bold text-lg truncate" :title="product.title">{{ product.title }}</div>
                <p class="text-sm text-gray-600 dark:text-gray-300 line-clamp-2 mt-2 flex-grow">{{ product.description }}</p>
                <template #footer>
                  <div class="flex items-center justify-between">
                    <span class="text-xl font-bold text-green-600 dark:text-green-400">{{ product.price }} ₽</span>
                    <UButton color="primary" size="sm" icon="i-heroicons-shopping-cart" pointer-events-none>Купить</UButton>
                  </div>
                </template>
              </UCard>
            </NuxtLink>
          </div>
        </div>
      </template>

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
    </div>

    <div v-else class="flex-grow flex flex-col">
      <div class="mb-6 flex justify-between items-center">
        <h2 class="text-2xl font-bold">
          Результаты по запросу: <span class="text-primary-500">«{{ route.query.q }}»</span>
        </h2>
        <UButton color="gray" variant="ghost" icon="i-heroicons-arrow-left" @click="router.push('/')">
          На главную
        </UButton>
      </div>

      <div v-if="searchPending" class="flex justify-center py-20">
        <UIcon name="i-heroicons-arrow-path" class="animate-spin w-10 h-10 text-primary-500" />
      </div>

      <div v-else-if="searchResults.length > 0" class="flex-grow flex flex-col">
        <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6 mb-10">
          <NuxtLink
            v-for="product in searchResults"
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
                  <img v-if="product.thumbnail_url" :src="product.thumbnail_url" @error="$event.target.src = product.image_url" :alt="product.title" class="w-full h-full object-cover transition-transform duration-300 hover:scale-105" />
                  <img v-else-if="product.image_url" :src="product.image_url" :alt="product.title" class="w-full h-full object-cover transition-transform duration-300 hover:scale-105" />
                  <UIcon v-else name="i-heroicons-photo" class="w-12 h-12 text-gray-300 dark:text-gray-600" />
                </div>
              </template>
              <div class="font-bold text-lg truncate" :title="product.title">{{ product.title }}</div>
              <p class="text-sm text-gray-600 dark:text-gray-300 line-clamp-2 mt-2 flex-grow">{{ product.description }}</p>
              <template #footer>
                <div class="flex items-center justify-between">
                  <span class="text-xl font-bold text-green-600 dark:text-green-400">{{ product.price }} ₽</span>
                  <UButton color="primary" size="sm" icon="i-heroicons-shopping-cart" pointer-events-none>Купить</UButton>
                </div>
              </template>
            </UCard>
          </NuxtLink>
        </div>

        <div class="flex justify-center mt-auto pb-8" v-if="searchTotal > itemsPerPage">
          <UPagination
            v-model="page"
            :total="searchTotal"
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
        <UButton class="mt-4" color="primary" variant="soft" @click="router.push('/')">
          Сбросить поиск
        </UButton>
      </div>
    </div>

  </UContainer>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const { $api } = useNuxtApp()
const itemsPerPage = 8

// Проверяем, есть ли запрос в URL
const isSearchActive = computed(() => !!route.query.q)

// --- 1. ЗАГРУЗКА ДАННЫХ: Витрина (Главная страница) ---
const { data: homeData, pending: homePending } = await useFetch('/api/home', {
  $fetch: $api
})
const popularCategories = computed(() => homeData.value?.categories || [])
const popularProducts = computed(() => homeData.value?.products || [])

// --- 2. ЗАГРУЗКА ДАННЫХ: Каталог/Поиск ---
const page = computed({
  get: () => Number(route.query.page) || 1,
  set: (val) => {
    router.push({ query: { ...route.query, page: val } })
  }
})
const currentOffset = computed(() => (page.value - 1) * itemsPerPage)

const { data: searchData, pending: searchPending } = await useFetch('/api/products', {
  $fetch: $api,
  query: {
    limit: itemsPerPage,
    offset: currentOffset,
    q: computed(() => route.query.q)
  },
  watch: [() => route.query.q, page]
})
const searchResults = computed(() => searchData.value?.items || [])
const searchTotal = computed(() => searchData.value?.total || 0)

// --- 3. Клик по категории ---
const searchByCategory = (categoryName) => {
  router.push({
    path: '/',
    query: {
      q: categoryName,
      page: 1
    }
  })
}

useHead({
  title: 'Твой Маркетплейс Цифровых Товаров | myMarket'
})
</script>
