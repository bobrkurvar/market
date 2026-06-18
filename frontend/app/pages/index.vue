<template>
  <UContainer class="relative py-8 min-h-screen flex flex-col">
    <div v-if="!isSearchActive" class="flex-grow flex flex-col gap-12">
      <div v-if="homePending" class="flex justify-center py-20">
        <UIcon name="i-heroicons-arrow-path" class="animate-spin w-10 h-10 text-primary-500" />
      </div>

      <template v-else>
        <section v-if="homeCategories.length > 0" class="space-y-6">
          <div class="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
            <div>
              <p class="text-sm font-semibold uppercase tracking-[0.2em] text-primary-500">Разделы</p>
              <h2 class="mt-2 text-3xl font-black tracking-tight text-gray-950 dark:text-white">Популярные категории</h2>
              <p class="mt-2 text-gray-500 dark:text-gray-400">Выбирай нужный раздел и переходи к товарам.</p>
            </div>

            <UButton
              v-if="hasMoreCategories"
              :loading="isLoadingCats"
              color="gray"
              variant="soft"
              size="lg"
              icon="i-heroicons-chevron-down"
              trailing
              class="rounded-xl"
              @click="loadMoreCategories"
            >
              Все категории
            </UButton>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            <NuxtLink
              v-for="category in homeCategories"
              :key="category.id"
              :to="`/categories/${category.slug}/${category.id}`"
              class="group block outline-none"
            >
              <UCard
                class="h-full overflow-hidden border border-gray-200/70 bg-white/90 shadow-sm transition-all duration-300 hover:-translate-y-1 hover:shadow-xl hover:ring-2 hover:ring-primary-500/40 dark:border-gray-800 dark:bg-gray-900/80"
                :ui="{ header: { padding: 'p-0 sm:p-0' }, body: { padding: 'p-4 sm:p-5' } }"
              >
                <template #header>
                  <div class="relative aspect-[16/10] w-full overflow-hidden bg-gray-100 dark:bg-gray-800">
                    <img
                      v-if="category.catalog_url"
                      :src="category.catalog_url"
                      :alt="category.name"
                      class="h-full w-full object-cover transition-transform duration-500 group-hover:scale-110"
                    />
                    <div
                      v-else
                      class="flex h-full w-full items-center justify-center bg-gradient-to-br from-primary-50 to-gray-100 dark:from-primary-950/40 dark:to-gray-900"
                    >
                      <UIcon name="i-heroicons-folder" class="h-16 w-16 text-primary-500" />
                    </div>
                    <div class="absolute inset-0 bg-gradient-to-t from-black/60 via-black/15 to-transparent" />
                    <div class="absolute bottom-4 left-4 right-4">
                      <h3 class="text-xl font-black leading-tight text-white drop-shadow line-clamp-2">
                        {{ getDisplayCategoryName(category) }}
                      </h3>
                    </div>
                  </div>
                </template>

                <div class="flex items-center justify-between gap-3">
                  <span class="text-sm font-medium text-gray-500 dark:text-gray-400">Перейти к товарам</span>
                  <span class="flex h-9 w-9 items-center justify-center rounded-full bg-primary-50 text-primary-500 transition-all duration-300 group-hover:bg-primary-500 group-hover:text-white dark:bg-primary-950/40">
                    <UIcon name="i-heroicons-arrow-right" class="h-5 w-5 transition-transform duration-300 group-hover:translate-x-0.5" />
                  </span>
                </div>
              </UCard>
            </NuxtLink>
          </div>
        </section>

        <section v-if="homeProducts.length > 0" class="space-y-6">
          <div class="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
            <div>
              <p class="text-sm font-semibold uppercase tracking-[0.2em] text-primary-500">Витрина</p>
              <h2 class="mt-2 text-3xl font-black tracking-tight text-gray-950 dark:text-white">Каталог товаров</h2>
              <p class="mt-2 text-gray-500 dark:text-gray-400">Популярные цифровые товары из каталога.</p>
            </div>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 xl:grid-cols-4 gap-6">
            <NuxtLink
              v-for="product in homeProducts"
              :key="product.id"
              :to="{ path: `/products/${product.slug}/${product.id}`, query: product.matched_variant_id ? { variant: product.matched_variant_id } : {} }"
              class="group block outline-none"
            >
              <UCard
                class="flex h-full flex-col overflow-hidden border border-gray-200/70 bg-white/90 shadow-sm transition-all duration-300 hover:-translate-y-1 hover:shadow-xl hover:ring-2 hover:ring-primary-500/40 dark:border-gray-800 dark:bg-gray-900/80"
                :ui="{ header: { padding: 'p-0 sm:p-0' }, body: { padding: 'p-4 sm:p-5 flex-grow flex flex-col' }, footer: { padding: 'p-4 sm:p-5 pt-0 sm:pt-0' } }"
              >
                <template #header>
                  <div class="relative aspect-[4/3] w-full overflow-hidden bg-gray-100 dark:bg-gray-800">
                    <img
                      v-if="product.catalog_url"
                      :src="product.catalog_url"
                      @error="$event.target.style.display='none'"
                      :alt="product.title"
                      class="h-full w-full object-cover transition-transform duration-500 group-hover:scale-110"
                    />
                    <img
                      v-else-if="product.image_url"
                      :src="product.image_url"
                      @error="$event.target.style.display='none'"
                      :alt="product.title"
                      class="h-full w-full object-cover transition-transform duration-500 group-hover:scale-110"
                    />
                    <div v-else class="flex h-full w-full items-center justify-center">
                      <UIcon name="i-heroicons-photo" class="h-14 w-14 text-gray-300 dark:text-gray-600" />
                    </div>
                    <div class="absolute left-3 top-3 rounded-full bg-white/90 px-3 py-1 text-xs font-bold text-gray-900 shadow-sm backdrop-blur dark:bg-gray-950/80 dark:text-white">
                      digital
                    </div>
                  </div>
                </template>

                <div v-if="product.category" class="mb-2 flex items-center gap-2 text-xs font-semibold text-primary-500">
                  <img v-if="product.category.search_url" :src="product.category.search_url" :alt="product.category.name" class="h-5 w-5 object-contain" />
                  <UIcon v-else name="i-heroicons-tag" class="h-4 w-4" />
                  <span class="truncate">{{ getDisplayCategoryName(product.category) }}</span>
                </div>

                <h3 class="text-lg font-black leading-snug text-gray-950 line-clamp-2 dark:text-white" :title="product.title">
                  {{ product.title }}
                </h3>
                <p class="mt-2 flex-grow text-sm leading-6 text-gray-500 line-clamp-3 dark:text-gray-400">
                  {{ product.description }}
                </p>

                <template #footer>
                  <div class="flex items-center justify-between gap-3">
                    <div>
                      <div class="text-xs text-gray-400">Цена</div>
                      <span class="text-2xl font-black text-green-600 dark:text-green-400">{{ formatPrice(product.price) }} ₽</span>
                    </div>
                    <UButton color="primary" size="md" icon="i-heroicons-shopping-cart" class="rounded-xl pointer-events-none">
                      Купить
                    </UButton>
                  </div>
                </template>
              </UCard>
            </NuxtLink>
          </div>

          <div v-if="hasMoreProducts" class="mt-8 flex justify-center">
            <UButton
              :loading="isLoadingProds"
              color="primary"
              variant="soft"
              size="lg"
              icon="i-heroicons-arrow-down"
              trailing
              class="rounded-xl px-6"
              @click="loadMoreProducts"
            >
              Показать ещё товары
            </UButton>
          </div>
        </section>
      </template>

      <section class="grid grid-cols-1 gap-5 border-t border-gray-200 pt-12 dark:border-gray-800 md:grid-cols-3">
        <div class="rounded-3xl border border-gray-200/70 bg-white p-6 text-center shadow-sm dark:border-gray-800 dark:bg-gray-900/80">
          <div class="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-primary-50 text-primary-500 dark:bg-primary-950/40">
            <UIcon name="i-heroicons-bolt" class="h-8 w-8" />
          </div>
          <h3 class="text-xl font-black">Моментальная выдача</h3>
          <p class="mt-3 text-sm leading-6 text-gray-500 dark:text-gray-400">Ключ активации появляется на экране и дублируется на почту сразу после оплаты.</p>
        </div>
        <div class="rounded-3xl border border-gray-200/70 bg-white p-6 text-center shadow-sm dark:border-gray-800 dark:bg-gray-900/80">
          <div class="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-emerald-50 text-emerald-500 dark:bg-emerald-950/30">
            <UIcon name="i-heroicons-shield-check" class="h-8 w-8" />
          </div>
          <h3 class="text-xl font-black">Безопасная сделка</h3>
          <p class="mt-3 text-sm leading-6 text-gray-500 dark:text-gray-400">Заказ, оплата и выдача товара проходят через понятный сценарий без лишней ручной работы.</p>
        </div>
        <div class="rounded-3xl border border-gray-200/70 bg-white p-6 text-center shadow-sm dark:border-gray-800 dark:bg-gray-900/80">
          <div class="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-violet-50 text-violet-500 dark:bg-violet-950/30">
            <UIcon name="i-heroicons-users" class="h-8 w-8" />
          </div>
          <h3 class="text-xl font-black">Сотни продавцов</h3>
          <p class="mt-3 text-sm leading-6 text-gray-500 dark:text-gray-400">Конкуренция рождает лучшие цены. Выбирай товары по описанию, рейтингу и категории.</p>
        </div>
      </section>
    </div>

    <div v-else class="flex-grow flex flex-col">
      <div class="mb-8 rounded-3xl border border-gray-200/70 bg-white p-6 shadow-sm dark:border-gray-800 dark:bg-gray-900/80">
        <div class="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div>
            <p class="text-sm font-semibold uppercase tracking-[0.2em] text-primary-500">Поиск</p>
            <h2 class="mt-2 text-3xl font-black tracking-tight text-gray-950 dark:text-white">
              Результаты по запросу: <span class="text-primary-500">«{{ route.query.q }}»</span>
            </h2>
            <p class="mt-2 text-gray-500 dark:text-gray-400">Используй фильтры, чтобы быстрее сузить выдачу.</p>
          </div>
          <UButton color="gray" variant="soft" icon="i-heroicons-arrow-left" class="rounded-xl" @click="router.push('/')">
            На главную
          </UButton>
        </div>
      </div>

      <div class="flex flex-col md:flex-row gap-8 flex-grow pb-10">
        <ProductFilters
          v-if="searchResults.length > 0 || hasActiveSearchFilters"
          :config="[
            { key: 'price', label: 'Цена', type: 'range' }
          ]"
        />

        <main class="flex-grow flex flex-col min-w-0">
          <div v-if="isInitialLoad" class="flex justify-center py-20">
            <UIcon name="i-heroicons-arrow-path" class="animate-spin w-10 h-10 text-primary-500" />
          </div>

          <div v-else-if="searchResults.length > 0" class="flex-grow flex flex-col">
            <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 xl:grid-cols-4 gap-6">
              <NuxtLink
                v-for="product in searchResults"
                :key="product.id"
                :to="{ path: `/products/${product.slug}/${product.id}`, query: product.matched_variant_id ? { variant: product.matched_variant_id } : {} }"
                class="group block outline-none"
              >
                <UCard
                  class="flex h-full flex-col overflow-hidden border border-gray-200/70 bg-white/90 shadow-sm transition-all duration-300 hover:-translate-y-1 hover:shadow-xl hover:ring-2 hover:ring-primary-500/40 dark:border-gray-800 dark:bg-gray-900/80"
                  :ui="{ header: { padding: 'p-0 sm:p-0' }, body: { padding: 'p-4 sm:p-5 flex-grow flex flex-col' }, footer: { padding: 'p-4 sm:p-5 pt-0 sm:pt-0' } }"
                >
                  <template #header>
                    <div class="relative aspect-[4/3] w-full overflow-hidden bg-gray-100 dark:bg-gray-800">
                      <img
                        v-if="product.catalog_url"
                        :src="product.catalog_url"
                        @error="$event.target.style.display='none'"
                        :alt="product.title"
                        class="h-full w-full object-cover transition-transform duration-500 group-hover:scale-110"
                      />
                      <img
                        v-else-if="product.image_url"
                        :src="product.image_url"
                        @error="$event.target.style.display='none'"
                        :alt="product.title"
                        class="h-full w-full object-cover transition-transform duration-500 group-hover:scale-110"
                      />
                      <div v-else class="flex h-full w-full items-center justify-center">
                        <UIcon name="i-heroicons-photo" class="h-14 w-14 text-gray-300 dark:text-gray-600" />
                      </div>
                    </div>
                  </template>

                  <div v-if="product.category" class="mb-2 flex items-center gap-2 text-xs font-semibold text-primary-500">
                    <img v-if="product.category.search_url" :src="product.category.search_url" :alt="product.category.name" class="h-5 w-5 object-contain" />
                    <UIcon v-else name="i-heroicons-tag" class="h-4 w-4" />
                    <span class="truncate">{{ getDisplayCategoryName(product.category) }}</span>
                  </div>

                  <h3 class="text-lg font-black leading-snug text-gray-950 line-clamp-2 dark:text-white" :title="product.title">
                    {{ product.title }}
                  </h3>
                  <p class="mt-2 flex-grow text-sm leading-6 text-gray-500 line-clamp-3 dark:text-gray-400">
                    {{ product.description }}
                  </p>

                  <template #footer>
                    <div class="flex items-center justify-between gap-3">
                      <div>
                        <div class="text-xs text-gray-400">Цена</div>
                        <span class="text-2xl font-black text-green-600 dark:text-green-400">{{ formatPrice(product.price) }} ₽</span>
                      </div>
                      <UButton color="primary" size="md" icon="i-heroicons-shopping-cart" class="rounded-xl pointer-events-none">
                        Купить
                      </UButton>
                    </div>
                  </template>
                </UCard>
              </NuxtLink>
            </div>

            <div v-if="isLoadingMore" class="flex justify-center mt-8">
              <UIcon name="i-heroicons-arrow-path" class="animate-spin w-8 h-8 text-primary-500" />
            </div>
          </div>

          <div v-else class="flex-grow rounded-3xl border border-dashed border-gray-300 bg-gray-50 px-6 py-20 text-center dark:border-gray-700 dark:bg-gray-900/60">
            <UIcon name="i-heroicons-face-frown" class="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 class="text-2xl font-black text-gray-950 dark:text-white">Ничего не найдено</h3>
            <p v-if="hasActiveSearchFilters" class="text-gray-500 mt-2">Попробуйте сбросить фильтр по цене.</p>
            <p v-else class="text-gray-500 mt-2">Попробуйте изменить поисковой запрос.</p>
          </div>
        </main>
      </div>
    </div>
  </UContainer>
</template>

<script setup>
import { computed, ref, watch, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter, useNuxtApp, useHead, useFetch } from '#imports'

const route = useRoute()
const router = useRouter()
const { $api } = useNuxtApp()

// --- ОБЩАЯ ЛОГИКА ---
const isSearchActive = computed(() => !!route.query.q)
const homeLimit = 8
const searchLimit = 8

// Вычисляем, есть ли активные фильтры цены (для отображения правильного текста "Ничего не найдено")
const hasActiveSearchFilters = computed(() => !!route.query.min_price || !!route.query.max_price)

const getDisplayCategoryName = (category) => {
  if (!category) return ''
  if (category.name.toLowerCase() === 'прочее' && category.parent_name) {
    return `${category.parent_name} — Прочее`
  }
  return category.name
}

const formatPrice = (price) => {
  return new Intl.NumberFormat('ru-RU', { maximumFractionDigits: 0 }).format(Number(price || 0))
}

// --- 1. ЗАГРУЗКА ДАННЫХ: Витрина (Главная страница) ---
const homeCategories = ref([])
const homeProducts = ref([])

const catOffset = ref(homeLimit)
const prodOffset = ref(homeLimit)

const hasMoreCategories = ref(true)
const hasMoreProducts = ref(true)

const isLoadingCats = ref(false)
const isLoadingProds = ref(false)

const { data: homeData, pending: homePending } = await useFetch('/api/home', {
  $fetch: $api,
  query: { limit: homeLimit, offset: 0 }
})

if (homeData.value) {
  homeCategories.value = homeData.value.categories || []
  homeProducts.value = homeData.value.products || []

  if (homeCategories.value.length < homeLimit) hasMoreCategories.value = false
  if (homeProducts.value.length < homeLimit) hasMoreProducts.value = false
}

const loadMoreCategories = async () => {
  isLoadingCats.value = true
  try {
    const res = await $api('/api/categories', {
      query: { limit: homeLimit, offset: catOffset.value }
    })

    const newCategories = res.items || res

    if (newCategories && newCategories.length > 0) {
      homeCategories.value.push(...newCategories)
      catOffset.value += homeLimit
      if (newCategories.length < homeLimit) hasMoreCategories.value = false
    } else {
      hasMoreCategories.value = false
    }
  } catch (error) {
    console.error('Ошибка при подгрузке категорий:', error)
  } finally {
    isLoadingCats.value = false
  }
}

const loadMoreProducts = async () => {
  isLoadingProds.value = true
  try {
    const res = await $api('/api/products', {
      query: { limit: homeLimit, offset: prodOffset.value }
    })

    const newProducts = res.items

    if (newProducts && newProducts.length > 0) {
      homeProducts.value.push(...newProducts)
      prodOffset.value += homeLimit
      if (newProducts.length < homeLimit) hasMoreProducts.value = false
    } else {
      hasMoreProducts.value = false
    }
  } catch (error) {
    console.error('Ошибка при подгрузке товаров:', error)
  } finally {
    isLoadingProds.value = false
  }
}

// --- 2. ЛОГИКА ПОИСКА (С поддержкой фильтров цены) ---
const searchResults = ref([])
const searchTotal = ref(0)
const page = ref(1)

const isInitialLoad = ref(false)
const isLoadingMore = ref(false)

const fetchSearchData = async (isLoadMore = false) => {
  if (!route.query.q) return

  if (isLoadMore) {
    isLoadingMore.value = true
  } else {
    isInitialLoad.value = true
  }

  try {
    const params = {
      limit: searchLimit,
      offset: (page.value - 1) * searchLimit,
      q: route.query.q,
      min_price: route.query.min_price || undefined,
      max_price: route.query.max_price || undefined
    }

    const res = await $api('/api/products', { query: params })

    if (isLoadMore) {
      searchResults.value.push(...res.items)
    } else {
      searchResults.value = res.items
    }
    searchTotal.value = res.total
  } catch (error) {
    console.error('Ошибка при поиске товаров:', error)
  } finally {
    isInitialLoad.value = false
    isLoadingMore.value = false
  }
}

watch(() => route.query, (newQuery) => {
  if (newQuery.q) {
    page.value = 1
    searchResults.value = []
    fetchSearchData()
  } else {
    searchResults.value = []
    searchTotal.value = 0
  }
}, { immediate: true, deep: true })

const handleScroll = () => {
  if (!isSearchActive.value || isInitialLoad.value || isLoadingMore.value) return
  if (searchResults.value.length >= searchTotal.value) return

  const bottomOfWindow = window.innerHeight + window.scrollY >= document.documentElement.offsetHeight - 300

  if (bottomOfWindow) {
    page.value++
    fetchSearchData(true)
  }
}

onMounted(() => {
  window.addEventListener('scroll', handleScroll)
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})

useHead({
  title: 'Твой Маркетплейс Цифровых Товаров | myMarket'
})
</script>
