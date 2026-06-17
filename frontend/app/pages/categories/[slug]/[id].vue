<template>
  <UContainer class="py-6 min-h-screen flex flex-col">
    <div class="mb-6 flex justify-between items-center">
      <UButton color="gray" variant="ghost" icon="i-heroicons-arrow-left" @click="router.push('/')">
        На главную
      </UButton>
    </div>

    <div v-if="categoryPending" class="flex justify-center py-20">
      <UIcon name="i-heroicons-arrow-path" class="animate-spin w-10 h-10 text-primary-500" />
    </div>

    <template v-else-if="category">
      <div class="mb-8">
        <h1 class="text-3xl font-bold">
          {{ category.parent_name ? `${category.parent_name} — ${category.name}` : category.name }}
        </h1>
        <p v-if="category.description" class="text-gray-500 mt-2">{{ category.description }}</p>
      </div>

      <div v-if="isFolder" class="flex-grow">
        <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
          <NuxtLink
            v-for="child in category.children"
            :key="child.id"
            :to="`/categories/${child.slug}/${child.id}`"
            class="block outline-none group"
          >
            <UCard
              class="flex flex-col h-full cursor-pointer transition-all duration-200 hover:ring-2 hover:ring-primary-500 hover:shadow-md text-center"
              :ui="{ body: { padding: 'p-6 flex flex-col items-center justify-center' } }"
            >
              <div class="w-16 h-16 mb-4 flex items-center justify-center bg-gray-50 dark:bg-gray-800 rounded-full group-hover:scale-110 transition-transform duration-300">
                <img v-if="child.catalog_url" :src="child.catalog_url" :alt="child.name" class="w-10 h-10 object-contain" />
                <UIcon v-else name="i-heroicons-folder" class="w-8 h-8 text-primary-500" />
              </div>
              <span class="font-bold text-gray-900 dark:text-white">{{ child.name }}</span>
            </UCard>
          </NuxtLink>
        </div>
      </div>

      <div v-else class="flex flex-col md:flex-row gap-8 flex-grow">

        <ProductFilters
          v-if="category.filter_config?.length && (productsTotal > 0 || hasActiveFilters)"
          :config="category.filter_config"
        />

        <main class="flex-grow flex flex-col min-w-0">
          <div v-if="isInitialLoad" class="flex justify-center py-10">
            <UIcon name="i-heroicons-arrow-path" class="animate-spin w-8 h-8 text-primary-500" />
          </div>

          <div v-else-if="products.length > 0" class="flex-grow flex flex-col">
            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 mb-10">
              <NuxtLink
                v-for="product in products"
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
                      <img v-if="product.catalog_url || product.image_url"
                           :src="product.catalog_url || product.image_url"
                           @error="$event.target.style.display='none'"
                           :alt="product.title"
                           class="w-full h-full object-cover transition-transform duration-300 hover:scale-105" />
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

            <div v-if="isLoadingMore" class="flex justify-center mt-auto pb-8">
              <UIcon name="i-heroicons-arrow-path" class="animate-spin w-8 h-8 text-primary-500" />
            </div>
          </div>

          <div v-else class="text-center py-16 bg-gray-50 dark:bg-gray-800 rounded-lg">
            <UIcon name="i-heroicons-archive-box" class="w-12 h-12 text-gray-400 mx-auto mb-3" />
            <h3 class="text-lg font-medium text-gray-900 dark:text-white">Товары не найдены</h3>
            <p v-if="hasActiveFilters" class="text-gray-500 text-sm mt-1">Попробуйте изменить или сбросить параметры фильтрации.</p>
            <p v-else class="text-gray-500 text-sm mt-1">В этой категории пока нет товаров.</p>
          </div>
        </main>
      </div>
    </template>

    <div v-else class="text-center py-20 flex-grow">
      <UIcon name="i-heroicons-face-frown" class="w-16 h-16 text-gray-400 mx-auto mb-4" />
      <h3 class="text-xl font-bold">Категория не найдена на сервере</h3>
    </div>
  </UContainer>
</template>

<script setup>
import { useRoute, useRouter } from 'vue-router'
import { computed, ref, watch, onMounted, onUnmounted } from 'vue'

const route = useRoute()
const router = useRouter()
const { $api } = useNuxtApp()

const categorySlug = route.params.slug
const categoryId = route.params.id

// --- СОСТОЯНИЕ СКРОЛЛА И ТОВАРОВ ---
const products = ref([])
const productsTotal = ref(0)
const offset = ref(0)
const itemsPerPage = 12

const isInitialLoad = ref(false)
const isLoadingMore = ref(false)

// --- 1. Загрузка категории ---
const { data: category, pending: categoryPending } = await useFetch(`/api/categories/${categorySlug}/${categoryId}`, {
  $fetch: $api
})

const isFolder = computed(() => {
  return category.value?.is_folder === true
})

// Простая проверка, есть ли параметры в URL (для вывода текста "Ничего не найдено")
const hasActiveFilters = computed(() => {
  return Object.keys(route.query).length > 0
})

// --- 2. Универсальная функция подгрузки товаров ---
const fetchProducts = async (isLoadMore = false) => {
  if (isFolder.value) return

  if (isLoadMore) {
    isLoadingMore.value = true
  } else {
    isInitialLoad.value = true
    offset.value = 0
  }

  try {
    // Вся магия фильтров теперь происходит здесь:
    // Мы просто берем параметры из URL (route.query) и отправляем их на бэкенд
    const params = {
      category_id: categoryId,
      limit: itemsPerPage,
      offset: offset.value,
      ...route.query
    }

    const res = await $api('/api/products', { query: params })

    if (isLoadMore) {
      products.value.push(...(res.items || []))
    } else {
      products.value = res.items || []
    }
    productsTotal.value = res.total || 0

  } catch (error) {
    console.error('Ошибка при загрузке товаров:', error)
  } finally {
    isLoadingMore.value = false
    isInitialLoad.value = false
  }
}

await fetchProducts()

// --- 3. Следим за URL ---
// Компонент ProductFilters меняет URL -> мы это видим и перезагружаем товары
watch(() => route.query, () => {
  if (!isFolder.value) {
    fetchProducts(false)
  }
}, { deep: true })

// --- ЛОГИКА БЕСКОНЕЧНОГО СКРОЛЛА ---
const handleScroll = () => {
  if (isFolder.value || isInitialLoad.value || isLoadingMore.value) return
  if (products.value.length >= productsTotal.value) return

  const bottomOfWindow = window.innerHeight + window.scrollY >= document.documentElement.offsetHeight - 300

  if (bottomOfWindow) {
    offset.value += itemsPerPage
    fetchProducts(true)
  }
}

onMounted(() => {
  window.addEventListener('scroll', handleScroll)
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})
</script>
