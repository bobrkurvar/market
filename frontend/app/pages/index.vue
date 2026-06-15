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
        <div class="mb-12" v-if="homeCategories.length > 0">
          <h2 class="text-2xl font-bold mb-6">Категории</h2>
          <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            <NuxtLink
              v-for="category in homeCategories"
              :key="category.id"
              :to="`/categories/${category.slug}/${category.id}`"
              class="block outline-none"
            >
              <UCard
                class="cursor-pointer hover:ring-2 hover:ring-primary-500 hover:shadow-md transition-all flex items-center justify-center text-center h-20"
                :ui="{ body: { padding: 'p-2 sm:p-4' } }"
              >
                <span class="font-semibold line-clamp-2">{{ getDisplayCategoryName(category) }}</span>
              </UCard>
            </NuxtLink>
          </div>
          <div class="mt-6 flex justify-center" v-if="hasMoreCategories">
            <UButton
              :loading="isLoadingCats"
              color="gray"
              variant="soft"
              @click="loadMoreCategories"
              icon="i-heroicons-chevron-down"
              trailing
            >
              Все категории
            </UButton>
          </div>
        </div>

        <div class="mb-12" v-if="homeProducts.length > 0">
          <h2 class="text-2xl font-bold mb-6">Каталог товаров</h2>
          <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
            <NuxtLink
              v-for="product in homeProducts"
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
                    <img v-if="product.catalog_url" :src="product.catalog_url" @error="$event.target.style.display='none'" :alt="product.title" class="w-full h-full object-cover transition-transform duration-300 hover:scale-105" />
                    <img v-else-if="product.image_url" :src="product.image_url" @error="$event.target.style.display='none'" :alt="product.title" class="w-full h-full object-cover transition-transform duration-300 hover:scale-105" />
                    <UIcon v-else name="i-heroicons-photo" class="w-12 h-12 text-gray-300 dark:text-gray-600" />
                  </div>
                </template>

                <div v-if="product.category" class="text-xs text-primary-500 font-medium mb-1">
                  {{ getDisplayCategoryName(product.category) }}
                </div>

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
          <div class="mt-8 flex justify-center" v-if="hasMoreProducts">
            <UButton
              :loading="isLoadingProds"
              color="primary"
              variant="soft"
              size="lg"
              @click="loadMoreProducts"
              icon="i-heroicons-arrow-down"
              trailing
            >
              Показать еще товары
            </UButton>
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

      <div v-if="isInitialLoad" class="flex justify-center py-20">
        <UIcon name="i-heroicons-arrow-path" class="animate-spin w-10 h-10 text-primary-500" />
      </div>

      <div v-else-if="searchResults.length > 0" class="flex-grow flex flex-col pb-10">
        <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
          <NuxtLink
            v-for="product in searchResults"
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
                  <img v-if="product.catalog_url" :src="product.catalog_url" @error="$event.target.style.display='none'" :alt="product.title" class="w-full h-full object-cover transition-transform duration-300 hover:scale-105" />
                  <img v-else-if="product.image_url" :src="product.image_url" @error="$event.target.style.display='none'" :alt="product.title" class="w-full h-full object-cover transition-transform duration-300 hover:scale-105" />
                  <UIcon v-else name="i-heroicons-photo" class="w-12 h-12 text-gray-300 dark:text-gray-600" />
                </div>
              </template>

              <div v-if="product.category" class="text-xs text-primary-500 font-medium mb-1">
                {{ getDisplayCategoryName(product.category) }}
              </div>

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

        <div v-if="isLoadingMore" class="flex justify-center mt-8">
          <UIcon name="i-heroicons-arrow-path" class="animate-spin w-8 h-8 text-primary-500" />
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
import { computed, ref, watch, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter, useNuxtApp, useHead, useFetch } from '#imports'

const route = useRoute()
const router = useRouter()
const { $api } = useNuxtApp()

// --- ОБЩАЯ ЛОГИКА ---
const isSearchActive = computed(() => !!route.query.q)
const homeLimit = 8 // Лимит и для категорий, и для товаров
const searchLimit = 8

// Функция маскировки "Прочее" под имя родителя
const getDisplayCategoryName = (category) => {
  if (!category) return '';
  if (category.name === 'Прочее' && category.parent) {
    return category.parent.name;
  }
  return category.name;
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

// Первичная загрузка
const { data: homeData, pending: homePending } = await useFetch('/api/home', {
  $fetch: $api,
  query: { limit: homeLimit, offset: 0 }
})

// Синхронизируем полученные данные с нашими реактивными переменными
if (homeData.value) {
  homeCategories.value = homeData.value.categories || []
  homeProducts.value = homeData.value.products || []

  // Если пришло меньше элементов, чем лимит — значит больше в базе нет
  if (homeCategories.value.length < homeLimit) hasMoreCategories.value = false
  if (homeProducts.value.length < homeLimit) hasMoreProducts.value = false
}

// Подгрузка категорий по кнопке
const loadMoreCategories = async () => {
  isLoadingCats.value = true;
  try {
    const res = await $api('/api/home', {
      query: { limit: homeLimit, offset: catOffset.value }
    });

    if (res.categories && res.categories.length > 0) {
      homeCategories.value.push(...res.categories);
      catOffset.value += homeLimit;
      if (res.categories.length < homeLimit) hasMoreCategories.value = false;
    } else {
      hasMoreCategories.value = false;
    }
  } catch (error) {
    console.error('Ошибка при подгрузке категорий:', error);
  } finally {
    isLoadingCats.value = false;
  }
}

// Подгрузка товаров по кнопке
const loadMoreProducts = async () => {
  isLoadingProds.value = true;
  try {
    const res = await $api('/api/home', {
      query: { limit: homeLimit, offset: prodOffset.value }
    });

    if (res.products && res.products.length > 0) {
      homeProducts.value.push(...res.products);
      prodOffset.value += homeLimit;
      if (res.products.length < homeLimit) hasMoreProducts.value = false;
    } else {
      hasMoreProducts.value = false;
    }
  } catch (error) {
    console.error('Ошибка при подгрузке товаров:', error);
  } finally {
    isLoadingProds.value = false;
  }
}

// --- 2. ЛОГИКА ПОИСКА (Бесконечная подгрузка при скролле) ---
const searchResults = ref([])
const searchTotal = ref(0)
const page = ref(1)

const isInitialLoad = ref(false)
const isLoadingMore = ref(false)

const fetchSearchData = async (isLoadMore = false) => {
  if (!route.query.q) return;

  if (isLoadMore) {
    isLoadingMore.value = true;
  } else {
    isInitialLoad.value = true;
  }

  try {
    const res = await $api('/api/products', {
      query: {
        limit: searchLimit,
        offset: (page.value - 1) * searchLimit,
        q: route.query.q
      }
    });

    if (isLoadMore) {
      searchResults.value.push(...res.items);
    } else {
      searchResults.value = res.items;
    }
    searchTotal.value = res.total;
  } catch (error) {
    console.error('Ошибка при поиске товаров:', error);
  } finally {
    isInitialLoad.value = false;
    isLoadingMore.value = false;
  }
}

watch(() => route.query.q, (newQuery) => {
  if (newQuery) {
    page.value = 1;
    searchResults.value = [];
    fetchSearchData();
  } else {
    searchResults.value = [];
    searchTotal.value = 0;
  }
}, { immediate: true })

const handleScroll = () => {
  if (!isSearchActive.value || isInitialLoad.value || isLoadingMore.value) return;
  if (searchResults.value.length >= searchTotal.value) return;

  const bottomOfWindow = window.innerHeight + window.scrollY >= document.documentElement.offsetHeight - 300;

  if (bottomOfWindow) {
    page.value++;
    fetchSearchData(true);
  }
}

onMounted(() => {
  window.addEventListener('scroll', handleScroll);
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll);
})

useHead({
  title: 'Твой Маркетплейс Цифровых Товаров | myMarket'
})
</script>
