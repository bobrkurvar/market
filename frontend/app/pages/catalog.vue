<template>
  <UContainer class="py-10">
    <div class="mb-8">
      <h1 class="text-3xl font-extrabold tracking-tight text-gray-900 dark:text-white sm:text-4xl">
        Каталог цифровых товаров
      </h1>
      <p class="text-gray-500 mt-2">Игры, ключи активации, подписки и игровая валюта</p>
    </div>

    <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6 mb-10">
      <NuxtLink
        v-for="product in products"
        :key="product.id"
        :to="`/products/${product.id}`"
        class="block outline-none"
      >
        <UCard
          class="flex flex-col justify-between h-full cursor-pointer transition-all duration-200 hover:ring-2 hover:ring-primary-500 hover:shadow-md"
        >
          <template #header>
            <div class="font-bold text-lg truncate">{{ product.title }}</div>
            <div class="text-xs text-gray-400 mt-1">{{ product.category }}</div>
          </template>

          <p class="text-sm text-gray-600 dark:text-gray-300 line-clamp-2">
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
  </UContainer>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const { $api } = useNuxtApp()
const itemsPerPage = 8

// 1. Оставляем реактивную страницу, которая синхронизируется с URL
const page = computed({
  get: () => Number(route.query.page) || 1,
  set: (val) => {
    router.push({ query: { ...route.query, page: val } })
  }
})

// 2. Вычисляем offset (тоже реактивно!)
const currentOffset = computed(() => (page.value - 1) * itemsPerPage)

// 3. Используем мощь useFetch!
const { data, pending, error } = await useFetch('/api/products', {
  $fetch: $api,
  query: {
    limit: itemsPerPage,
    offset: currentOffset // <-- сам следит за этой переменной
  }
})

// Если data.value есть, берем items, иначе пустой массив
const products = computed(() => data.value?.items || [])
const totalItems = computed(() => data.value?.total || 0)

useHead({
  title: 'Каталог цифровых товаров | myMarket'
})
</script>
