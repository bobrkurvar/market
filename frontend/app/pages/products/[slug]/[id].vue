<template>
  <UContainer class="py-10">
    <div v-if="pending" class="flex justify-center py-20">
      <UIcon name="i-heroicons-arrow-path" class="w-10 h-10 animate-spin text-primary-500" />
    </div>

    <div v-else-if="product" class="grid grid-cols-1 lg:grid-cols-12 gap-10">

      <div class="lg:col-span-7 space-y-8">

        <div class="flex flex-col sm:flex-row gap-6">

          <div class="w-full sm:w-64 md:w-72 flex-shrink-0 aspect-square rounded-2xl overflow-hidden bg-gray-100 dark:bg-gray-800 border border-gray-200 dark:border-gray-800 shadow-sm relative group flex items-center justify-center">
            <img
              v-if="product.detail_url"
              :src="product.detail_url"
              :alt="product.title"
              class="w-full h-full object-cover transition-transform duration-500 group-hover:scale-[1.02]"
            />
            <div v-else class="flex flex-col items-center justify-center text-gray-400 dark:text-gray-500">
              <UIcon name="i-heroicons-photo" class="w-12 h-12 mb-2" />
              <span class="text-sm font-medium">Нет фото</span>
            </div>
          </div>

          <div class="flex flex-col justify-center py-2">
            <h1 class="text-2xl sm:text-3xl font-extrabold text-gray-900 dark:text-white leading-tight">
              {{ product.title }}
            </h1>

            <div class="mt-4 space-y-2 text-sm text-gray-500 dark:text-gray-400">
              <p class="flex items-center gap-2">
                <UIcon name="i-heroicons-user-circle" class="w-5 h-5 text-gray-400" />
                Продавец: <span class="font-bold text-gray-900 dark:text-gray-200">{{ product.seller_username || 'Неизвестно' }}</span>
              </p>
              <p class="flex items-center gap-2">
                <UIcon name="i-heroicons-bolt" class="w-5 h-5 text-amber-500" />
                Автоматическая доставка
              </p>
            </div>
          </div>

        </div>

        <div class="prose dark:prose-invert max-w-none bg-white dark:bg-gray-900 p-6 sm:p-8 rounded-2xl border border-gray-200 dark:border-gray-800 shadow-sm">
          <h3 class="text-xl font-bold mb-4">Описание товара</h3>
          <p class="whitespace-pre-line text-gray-700 dark:text-gray-300 leading-relaxed">
            {{ product.description }}
          </p>
        </div>
      </div>

      <div class="lg:col-span-5">
        <UCard class="sticky top-24 shadow-md ring-1 ring-gray-200 dark:ring-gray-800" :ui="{ body: { padding: 'p-6 sm:p-8' } }">

          <div class="mb-8 pb-6 border-b border-gray-100 dark:border-gray-800">
            <span class="text-sm font-medium text-gray-500">Итоговая стоимость</span>
            <div class="text-4xl font-black text-green-600 dark:text-green-400 mt-1">
              {{ selectedVariant?.price || 0 }} ₽
            </div>
          </div>

          <div class="mb-8" v-if="product.variants?.length > 0">
            <h3 class="text-sm font-bold text-gray-900 dark:text-white mb-4 uppercase tracking-wider">
              Выберите опцию
            </h3>

            <div class="space-y-3">
              <label
                v-for="variant in product.variants"
                :key="variant.id"
                class="flex items-start p-4 border rounded-xl cursor-pointer transition-all duration-200"
                :class="selectedVariant?.id === variant.id
                  ? 'border-primary-500 bg-primary-50 dark:bg-primary-950/30 ring-2 ring-primary-500'
                  : 'border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800'"
              >
                <div class="flex items-center h-5 mt-0.5">
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
                      {{ key }}: <span class="text-gray-500 dark:text-gray-400">{{ val }}</span>
                    </div>
                  </div>
                  <div v-else class="text-sm font-medium text-gray-900 dark:text-white">
                    Стандартное издание
                  </div>
                </div>

                <div class="text-base font-bold text-gray-900 dark:text-white ml-4">
                  {{ variant.price }} ₽
                </div>
              </label>
            </div>
          </div>

          <UButton
            size="xl"
            block
            color="primary"
            icon="i-heroicons-shopping-bag"
            :disabled="!selectedVariant"
            @click="buyProduct"
            class="font-bold text-base shadow-sm"
          >
            Купить сейчас
          </UButton>

          <p class="text-xs text-center text-gray-500 mt-4 flex items-center justify-center gap-1">
            <UIcon name="i-heroicons-shield-check" class="w-4 h-4" />
            Безопасная сделка. Мгновенная доставка.
          </p>
        </UCard>
      </div>
    </div>

    <div v-else class="text-center py-20">
      <UIcon name="i-heroicons-archive-box-x-mark" class="w-20 h-20 mx-auto text-gray-300 dark:text-gray-700 mb-4" />
      <h2 class="text-2xl font-bold text-gray-900 dark:text-white">Товар не найден</h2>
      <p class="text-gray-500 mt-2 mb-6">Возможно, он был удален или ссылка недействительна.</p>
      <UButton to="/" size="lg" color="gray" variant="solid">Вернуться в каталог</UButton>
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
