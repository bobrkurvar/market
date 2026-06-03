<template>
  <UContainer class="py-10">
    <div v-if="pending" class="flex justify-center py-20">
      <UIcon name="i-heroicons-arrow-path" class="w-10 h-10 animate-spin text-primary-500" />
    </div>

    <div v-else-if="product" class="grid grid-cols-1 lg:grid-cols-12 gap-10">

      <div class="lg:col-span-7 space-y-6">
        <div>
          <h1 class="text-3xl font-extrabold text-gray-900 dark:text-white sm:text-4xl">
            {{ product.title }}
          </h1>
          <p class="text-sm text-gray-500 mt-2">Продавец: {{ product.seller_username }}</p>
        </div>

        <div class="prose dark:prose-invert max-w-none">
          <h3 class="text-lg font-semibold">Описание</h3>
          <p class="whitespace-pre-line text-gray-700 dark:text-gray-300">
            {{ product.description }}
          </p>
        </div>
      </div>

      <div class="lg:col-span-5">
        <UCard class="sticky top-10">

          <div class="mb-6">
            <span class="text-sm text-gray-500">Итоговая стоимость</span>
            <div class="text-4xl font-extrabold text-green-600 dark:text-green-400">
              {{ selectedVariant?.price || 0 }} ₽
            </div>
          </div>

          <div class="mb-8" v-if="product.variants?.length > 0">
            <h3 class="text-sm font-semibold text-gray-900 dark:text-white mb-3 uppercase tracking-wider">
              Выберите опцию
            </h3>

            <div class="space-y-3">
              <label
                v-for="variant in product.variants"
                :key="variant.id"
                class="flex items-start p-4 border rounded-xl cursor-pointer transition-all duration-200"
                :class="selectedVariant?.id === variant.id
                  ? 'border-primary-500 bg-primary-50 dark:bg-primary-950/30 ring-1 ring-primary-500'
                  : 'border-gray-200 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-900'"
              >
                <div class="flex items-center h-5">
                  <input
                    type="radio"
                    name="variant"
                    :value="variant"
                    v-model="selectedVariant"
                    class="w-4 h-4 text-primary-600 focus:ring-primary-500 border-gray-300"
                  />
                </div>

                <div class="ml-3 flex-1">
                  <div v-if="variant.attributes && Object.keys(variant.attributes).length > 0">
                    <div v-for="(val, key) in variant.attributes" :key="key" class="text-sm font-medium text-gray-900 dark:text-white">
                      {{ key }}: <span class="text-gray-500">{{ val }}</span>
                    </div>
                  </div>
                  <div v-else class="text-sm font-medium text-gray-900 dark:text-white">
                    Стандартное издание
                  </div>
                </div>

                <div class="text-sm font-bold text-gray-900 dark:text-white ml-4">
                  {{ variant.price }} ₽
                </div>
              </label>
            </div>
          </div>

          <UButton
            size="xl"
            block
            color="primary"
            icon="i-heroicons-credit-card"
            :disabled="!selectedVariant"
            @click="buyProduct"
          >
            Купить сейчас
          </UButton>
        </UCard>
      </div>
    </div>

    <div v-else class="text-center py-20">
      <UIcon name="i-heroicons-archive-box-x-mark" class="w-16 h-16 mx-auto text-gray-400 mb-4" />
      <h2 class="text-2xl font-bold text-gray-900 dark:text-white">Товар не найден</h2>
      <UButton to="/products" variant="ghost" class="mt-4">Вернуться в каталог</UButton>
    </div>
  </UContainer>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const { $api } = useNuxtApp()
const toast = useToast()

const productId = route.params.id
const slug = route.params.slug

// Загружаем данные конкретного товара
const { data: product, pending } = await useFetch(`/api/products/${slug}/${productId}`, {
  $fetch: $api
})

// Храним выбранный вариант
const selectedVariant = ref(null)

// Магия реактивности: как только товар загрузился, автоматически выбираем первую опцию
watch(product, (newProduct) => {
  if (newProduct && newProduct.variants?.length > 0) {
    selectedVariant.value = newProduct.variants[0]
  }
}, { immediate: true })

const buyProduct = () => {
  toast.add({
    title: 'Оформление заказа',
    description: `Переход к оплате варианта #${selectedVariant.value.id} за ${selectedVariant.value.price} ₽`,
    color: 'green'
  })
  // Здесь будет логика создания заказа (переход в корзину или на платежный шлюз)
}

// Динамический заголовок вкладки браузера
useHead({
  title: computed(() => product.value ? `${product.value.title} | myMarket` : 'Загрузка товара...')
})
</script>
