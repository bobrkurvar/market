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
        <h1 class="text-3xl font-bold">{{ category.name }}</h1>
        <p v-if="category.description" class="text-gray-500 mt-2">{{ category.description }}</p>
      </div>

      <div v-if="productsPending" class="flex justify-center py-10">
        <UIcon name="i-heroicons-arrow-path" class="animate-spin w-8 h-8 text-primary-500" />
      </div>

      <div v-else-if="products.length > 0" class="flex-grow flex flex-col">
        <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6 mb-10">
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
                  <img v-if="product.catalog_url"
                       :src="product.catalog_url"
                       @error="$event.target.style.display='none'"
                       :alt="product.title"
                       class="w-full h-full object-cover transition-transform duration-300 hover:scale-105" />

                  <img v-else-if="product.image_url"
                       :src="product.image_url"
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

        <div class="flex justify-center mt-auto pb-8" v-if="productsTotal > itemsPerPage">
          <UPagination
            v-model="page"
            :total="productsTotal"
            :page-count="itemsPerPage"
            :prev-button="{ icon: 'i-heroicons-arrow-small-left', color: 'gray', variant: 'outline' }"
            :next-button="{ icon: 'i-heroicons-arrow-small-right', color: 'gray', variant: 'outline' }"
          />
        </div>
      </div>

      <div v-else class="text-center py-16 bg-gray-50 dark:bg-gray-800 rounded-lg">
        <UIcon name="i-heroicons-archive-box" class="w-12 h-12 text-gray-400 mx-auto mb-3" />
        <h3 class="text-lg font-medium text-gray-900 dark:text-white">В этой категории пока пусто</h3>
        <p class="text-gray-500 text-sm mt-1">Скоро здесь появятся новые товары.</p>
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
import { computed } from 'vue'

const route = useRoute()
const router = useRouter()
const { $api } = useNuxtApp()

// Параметры
const categorySlug = route.params.slug
const categoryId = route.params.id
const itemsPerPage = 8

const page = computed({
  get: () => Number(route.query.page) || 1,
  set: (val) => {
    router.push({ query: { ...route.query, page: val } })
  }
})
const currentOffset = computed(() => (page.value - 1) * itemsPerPage)

// 1. Запрос на получение информации о категории
const { data: category, pending: categoryPending } = await useFetch(`/api/categories/${categorySlug}/${categoryId}`, {
  $fetch: $api
})

// 2. Запрос на получение списка товаров для этой категории
const { data: productsData, pending: productsPending } = await useFetch('/api/products', {
  $fetch: $api,
  query: {
    category_id: categoryId, // <-- Передаем ID категории для фильтрации
    limit: itemsPerPage,
    offset: currentOffset
  },
  watch: [page] // перезагружать при смене страницы
})

const products = computed(() => productsData.value?.items || [])
const productsTotal = computed(() => productsData.value?.total || 0)

useHead({
  title: computed(() => category.value ? `${category.value.name} | myMarket` : 'Категория | myMarket')
})
</script>
