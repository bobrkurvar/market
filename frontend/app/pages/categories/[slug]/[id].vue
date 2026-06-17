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
        <aside
          v-if="category.filter_config?.length && (productsTotal > 0 || hasActiveFilters)"
          class="w-full md:w-64 flex-shrink-0"
        >
          <UCard :ui="{ body: { padding: 'p-4 sm:p-5' } }">
            <template #header>
              <div class="flex justify-between items-center">
                <h3 class="font-bold text-lg">Фильтры</h3>
                <UButton
                  v-if="hasActiveFilters"
                  color="gray"
                  variant="ghost"
                  size="xs"
                  @click="clearFilters"
                >
                  Сбросить
                </UButton>
              </div>
            </template>

            <div class="space-y-6">
              <div v-for="filter in category.filter_config" :key="filter.key" class="border-b border-gray-100 dark:border-gray-800 pb-4 last:border-0 last:pb-0">
                <h4 class="font-medium text-sm mb-3">{{ filter.label }}</h4>

                <div v-if="filter.type === 'checkbox'" class="space-y-2">
                  <UCheckbox
                    v-for="option in filter.options"
                    :key="option"
                    :label="option"
                    :model-value="activeFilters[filter.key]?.includes(option)"
                    @update:model-value="toggleCheckbox(filter.key, option)"
                  />
                </div>

                <div v-else-if="filter.type === 'radio'" class="space-y-2">
                  <URadio
                    v-for="option in filter.options"
                    :key="option"
                    v-model="activeFilters[filter.key]"
                    :value="option"
                    :label="option"
                  />
                </div>

                <div v-else-if="filter.type === 'select'">
                  <USelectMenu
                    v-model="activeFilters[filter.key]"
                    :options="filter.options"
                    placeholder="Выберите..."
                    clearable
                  />
                </div>

                <div v-else-if="filter.type === 'range'" class="flex items-center space-x-2">
                  <UInput
                    v-model="activeFilters[`${filter.key}_min`]"
                    type="number"
                    placeholder="От"
                    class="w-full"
                  />
                  <span class="text-gray-400">-</span>
                  <UInput
                    v-model="activeFilters[`${filter.key}_max`]"
                    type="number"
                    placeholder="До"
                    class="w-full"
                  />
                </div>

              </div>
            </div>
          </UCard>
        </aside>

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

// --- СОСТОЯНИЕ ФИЛЬТРОВ И СКРОЛЛА ---
const activeFilters = ref({})
const products = ref([])
const productsTotal = ref(0)
const offset = ref(0)
const itemsPerPage = 12

const isInitialLoad = ref(false)
const isLoadingMore = ref(false)

// --- 1. Загрузка категории и инициализация фильтров ---
const { data: category, pending: categoryPending } = await useFetch(`/api/categories/${categorySlug}/${categoryId}`, {
  $fetch: $api,
  onResponse({ response }) {
    const catData = response._data
    if (catData && catData.filter_config) {
      catData.filter_config.forEach(filter => {
        if (filter.type === 'checkbox') {
          let urlVal = route.query[filter.key]
          if (urlVal) {
            activeFilters.value[filter.key] = typeof urlVal === 'string' ? urlVal.split(',') : urlVal
          } else {
            activeFilters.value[filter.key] = []
          }
        } else if (filter.type === 'range') {
          activeFilters.value[`${filter.key}_min`] = route.query[`${filter.key}_min`] || undefined
          activeFilters.value[`${filter.key}_max`] = route.query[`${filter.key}_max`] || undefined
        } else {
          activeFilters.value[filter.key] = route.query[filter.key] || undefined
        }
      })
    }
  }
})

// Проверяем статус напрямую через флаг от бэкенда
const isFolder = computed(() => {
  return category.value?.is_folder === true
})

// --- 2. Ручное управление массивами для UCheckbox ---
const toggleCheckbox = (filterKey, option) => {
  const currentArray = activeFilters.value[filterKey] || []
  if (currentArray.includes(option)) {
    activeFilters.value[filterKey] = currentArray.filter(v => v !== option)
  } else {
    activeFilters.value[filterKey] = [...currentArray, option]
  }
}

// --- 3. Универсальная функция подгрузки товаров ---
const fetchProducts = async (isLoadMore = false) => {
  if (isFolder.value) return

  if (isLoadMore) {
    isLoadingMore.value = true
  } else {
    isInitialLoad.value = true
    offset.value = 0
  }

  try {
    const params = {
      category_id: categoryId,
      limit: itemsPerPage,
      offset: offset.value
    }

    for (const [key, value] of Object.entries(activeFilters.value)) {
      if (value !== undefined && value !== null && value !== '') {
        if (Array.isArray(value)) {
          if (value.length > 0) params[key] = value
        } else {
          params[key] = value
        }
      }
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

// --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ---
const hasActiveFilters = computed(() => {
  return Object.values(activeFilters.value).some(val => {
    if (Array.isArray(val)) return val.length > 0
    return val !== undefined && val !== null && val !== ''
  })
})

const clearFilters = () => {
  for (const key in activeFilters.value) {
    if (Array.isArray(activeFilters.value[key])) {
      activeFilters.value[key] = []
    } else {
      activeFilters.value[key] = undefined
    }
  }
}

watch(() => activeFilters.value, (newFilters, oldFilters) => {
  if (isFolder.value) return

  if (Object.keys(oldFilters).length > 0) {
    const query = {}

    for (const [key, value] of Object.entries(newFilters)) {
       if (value !== undefined && value !== null && value !== '') {
          if (Array.isArray(value)) {
            if (value.length > 0) query[key] = value.join(',')
          } else {
            query[key] = value
          }
       }
    }

    router.replace({ query })
    fetchProducts(false)
  }
}, { deep: true })

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
