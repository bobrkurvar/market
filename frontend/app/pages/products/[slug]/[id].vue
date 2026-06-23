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

            <div class="mt-4 space-y-3 text-sm text-gray-500 dark:text-gray-400">
              <div class="flex flex-wrap items-center gap-3">
                <p class="flex items-center gap-2 text-gray-600 dark:text-gray-400">
                  <UIcon name="i-heroicons-user-circle" class="w-5 h-5" />
                  Продавец:
                  <span class="font-bold text-gray-900 dark:text-gray-200">
                    {{ product.seller?.username || 'Неизвестно' }}
                  </span>
                </p>

                <UBadge v-if="product.seller?.rating" color="amber" variant="subtle" size="sm" class="flex items-center gap-1 font-bold">
                  <UIcon name="i-heroicons-star-solid" class="w-3.5 h-3.5" />
                  {{ product.seller.rating }}
                  <span v-if="product.seller?.reviews_count" class="text-amber-700/60 dark:text-amber-400/60 text-xs font-normal ml-0.5">
                    ({{ product.seller.reviews_count }})
                  </span>
                </UBadge>
                <UBadge v-else color="gray" variant="subtle" size="sm" class="flex items-center gap-1 font-medium text-gray-500">
                  <UIcon name="i-heroicons-star" class="w-3.5 h-3.5" />
                  Нет оценок
                </UBadge>

                <UBadge color="emerald" variant="subtle" size="sm" class="flex items-center gap-1 font-medium">
                  <UIcon name="i-heroicons-check-badge" class="w-3.5 h-3.5" />
                  {{ product.seller?.sales_count || 0 }} продаж
                </UBadge>
              </div>

              <div v-if="selectedVariant" class="mt-2">
                <p v-if="selectedVariant.stock === -1" class="flex items-center gap-2 text-sm">
                  <UIcon name="i-heroicons-bolt" class="w-5 h-5 text-amber-500" />
                  Автоматическая доставка
                </p>
                <p v-else class="flex items-center gap-2 text-sm">
                  <UIcon name="i-heroicons-clock" class="w-5 h-5 text-blue-500" />
                  Ручная выдача
                </p>
              </div>

            </div>
          </div>
        </div>

        <div class="prose dark:prose-invert max-w-none bg-white dark:bg-gray-900 p-6 sm:p-8 rounded-2xl border border-gray-200 dark:border-gray-800 shadow-sm">
          <h3 class="text-xl font-bold mb-4">Описание товара</h3>
          <p class="whitespace-pre-line text-gray-700 dark:text-gray-300 leading-relaxed">
            {{ product.description }}
          </p>
        </div>

        <div class="bg-white dark:bg-gray-900 p-6 sm:p-8 rounded-2xl border border-gray-200 dark:border-gray-800 shadow-sm">
          <h3 class="text-xl font-bold mb-6 flex items-center gap-2">
            Отзывы покупателей
            <span v-if="reviews.length" class="text-sm font-normal text-gray-500 bg-gray-100 dark:bg-gray-800 px-2 py-0.5 rounded-full">
              {{ reviews.length }} {{ hasMoreReviews ? '+' : '' }}
            </span>
          </h3>

          <div v-if="reviews.length === 0 && !isLoadingReviews" class="text-center py-10">
            <UIcon name="i-heroicons-chat-bubble-left-ellipsis" class="w-12 h-12 mx-auto text-gray-300 dark:text-gray-700 mb-3" />
            <p class="text-gray-500 dark:text-gray-400">У этого товара пока нет отзывов. Станьте первым!</p>
          </div>

          <div v-else class="space-y-6">
            <div v-for="(review, index) in reviews" :key="index" class="border-b border-gray-100 dark:border-gray-800 last:border-0 pb-6 last:pb-0">
              <div class="flex items-center gap-1 mb-2">
                <UIcon
                  v-for="i in 5"
                  :key="i"
                  name="i-heroicons-star-20-solid"
                  class="w-5 h-5"
                  :class="i <= review.rating ? 'text-amber-400' : 'text-gray-200 dark:text-gray-700'"
                />
              </div>
              <p class="text-gray-700 dark:text-gray-300 leading-relaxed">
                {{ review.comment || 'Покупатель не оставил текстовый комментарий.' }}
              </p>
            </div>
          </div>

          <div v-if="isLoadingReviews" class="flex justify-center mt-6">
            <UIcon name="i-heroicons-arrow-path" class="w-8 h-8 animate-spin text-primary-500" />
          </div>
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
              <template v-for="variant in product.variants" :key="variant.id">
                <label
                  v-if="variant.is_active !== false"
                  class="flex items-start p-4 border rounded-xl transition-all duration-200"
                  :class="[
                    variant.items_count === 0
                      ? 'opacity-50 cursor-not-allowed bg-gray-50 dark:bg-gray-800/50 border-gray-200 dark:border-gray-800'
                      : 'cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800',
                    selectedVariant?.id === variant.id && variant.items_count !== 0
                      ? 'border-primary-500 bg-primary-50 dark:bg-primary-950/30 ring-2 ring-primary-500'
                      : 'border-gray-200 dark:border-gray-700'
                  ]"
                >
                  <div class="flex items-center h-5 mt-0.5">
                    <input
                      type="radio"
                      name="variant"
                      :value="variant"
                      v-model="selectedVariant"
                      :disabled="variant.items_count === 0"
                      class="w-4 h-4 text-primary-600 focus:ring-primary-500 border-gray-300 disabled:opacity-50"
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

                    <div class="mt-1.5 text-xs font-bold" :class="getStockStatus(variant.items_count).color">
                      {{ getStockStatus(variant.items_count).text }}
                    </div>
                  </div>

                  <div class="text-base font-bold text-gray-900 dark:text-white ml-4">
                    {{ variant.price }} ₽
                  </div>
                </label>
              </template>
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
            Безопасная сделка. {{ selectedVariant?.stock === -1 ? 'Мгновенная доставка.' : 'Гарантия возврата.' }}
          </p>
        </UCard>
      </div>
    </div>

    <div v-else class="text-center py-20">
      <UIcon name="i-heroicons-archive-box-x-mark" class="w-20 h-20 mx-auto text-gray-300 dark:text-gray-700 mb-4" />
      <h2 class="text-2xl font-bold text-gray-900 dark:text-white">Товар не найден</h2>
      <p class="text-gray-500 mt-2 mb-6">Возможно, он был удален, закончился или ссылка недействительна.</p>
      <UButton to="/" size="lg" color="gray" variant="solid">Вернуться в каталог</UButton>
    </div>

    <Teleport to="body">
      <div v-if="isPaymentModalOpen" class="fixed inset-0 z-[100] flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
        <UCard class="w-full max-w-md shadow-2xl" :ui="{ ring: '', divide: 'divide-y divide-gray-100 dark:divide-gray-800' }">
          <div class="text-center py-8 px-4">

            <div v-if="paymentStep === 'creating' || paymentStep === 'waiting'">
              <UIcon name="i-heroicons-arrow-path" class="w-16 h-16 animate-spin text-primary-500 mx-auto mb-6" />
              <h3 class="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                {{ paymentStep === 'creating' ? 'Создаем заказ...' : 'Генерируем счет...' }}
              </h3>
              <p class="text-gray-500 dark:text-gray-400 animate-pulse">
                Пожалуйста, не закрывайте страницу.
              </p>
            </div>

            <div v-else-if="paymentStep === 'payment_ready'">
              <div class="w-20 h-20 bg-blue-100 dark:bg-blue-900/30 rounded-full flex items-center justify-center mx-auto mb-6">
                <UIcon name="i-heroicons-credit-card" class="w-10 h-10 text-blue-600 dark:text-blue-400" />
              </div>
              <h3 class="text-2xl font-bold text-gray-900 dark:text-white mb-2">Заказ готов к оплате</h3>
              <p class="text-gray-500 dark:text-gray-400 mb-8">Сумма к оплате: <span class="font-bold text-gray-900 dark:text-white">{{ selectedVariant?.price }} ₽</span></p>

              <UButton
                size="xl"
                color="blue"
                block
                @click="simulatePayment"
                icon="i-heroicons-banknotes"
              >
                Оплатить (Тестовый режим)
              </UButton>
              <UButton variant="ghost" color="gray" block class="mt-3" @click="isPaymentModalOpen = false">
                Отмена
              </UButton>
            </div>

            <div v-else-if="paymentStep === 'processing_payment'">
              <UIcon name="i-heroicons-arrow-path" class="w-16 h-16 animate-spin text-green-500 mx-auto mb-6" />
              <h3 class="text-xl font-bold text-gray-900 dark:text-white mb-2">Обработка платежа...</h3>
              <p class="text-gray-500 dark:text-gray-400 animate-pulse">Связываемся с банком.</p>
            </div>

            <div v-else-if="paymentStep === 'success'">
              <div class="w-20 h-20 bg-green-100 dark:bg-green-900/30 rounded-full flex items-center justify-center mx-auto mb-6">
                <UIcon name="i-heroicons-check" class="w-10 h-10 text-green-600 dark:text-green-400" />
              </div>
              <h3 class="text-2xl font-bold text-gray-900 dark:text-white mb-2">Оплата прошла успешно!</h3>
              <p class="text-gray-500 dark:text-gray-400 mb-8">Деньги зачислены. Товар зарезервирован за вами.</p>

              <UButton
                size="xl"
                color="primary"
                block
                :to="`/profile/orders/${createdOrderId}`"
                icon="i-heroicons-chat-bubble-left-right"
              >
                Получить товар и открыть чат
              </UButton>
            </div>

            <div v-else-if="paymentStep === 'error'">
              <div class="w-20 h-20 bg-red-100 dark:bg-red-900/30 rounded-full flex items-center justify-center mx-auto mb-6">
                <UIcon name="i-heroicons-x-mark" class="w-10 h-10 text-red-600 dark:text-red-400" />
              </div>
              <h3 class="text-2xl font-bold text-gray-900 dark:text-white mb-2">Произошла ошибка</h3>
              <p class="text-gray-500 dark:text-gray-400 mb-8">{{ paymentErrorMsg }}</p>

              <UButton size="lg" color="primary" block @click="isPaymentModalOpen = false">
                Закрыть
              </UButton>
            </div>

          </div>
        </UCard>
      </div>
    </Teleport>

  </UContainer>
</template>

<script setup>
import { ref, watch, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { useNuxtApp, useToast, useHead, useFetch } from '#imports'

const route = useRoute()
const { $api } = useNuxtApp()
const toast = useToast()

const productId = route.params.id
const slug = route.params.slug

// Загружаем данные конкретного товара (SEO-дружелюбно)
const { data: product, pending } = await useFetch(`/api/products/${slug}/${productId}`, {
  $fetch: $api
})

const selectedVariant = ref(null)

// --- ОТЗЫВЫ И ПАГИНАЦИЯ ---
const reviews = ref([])
const reviewsLimit = 10
const reviewsOffset = ref(0)
const hasMoreReviews = ref(true)
const isLoadingReviews = ref(false)

const loadReviews = async () => {
  if (isLoadingReviews.value || !hasMoreReviews.value) return

  isLoadingReviews.value = true
  try {
    const fetched = await $api(`/api/products/${slug}/${productId}/reviews`, {
      query: { limit: reviewsLimit, offset: reviewsOffset.value }
    })

    if (fetched && fetched.length > 0) {
      reviews.value.push(...fetched)
      reviewsOffset.value += reviewsLimit
      // Если пришло меньше чем мы просили, значит это конец
      if (fetched.length < reviewsLimit) {
        hasMoreReviews.value = false
      }
    } else {
      hasMoreReviews.value = false
    }
  } catch (error) {
    console.error('Ошибка при загрузке отзывов:', error)
  } finally {
    isLoadingReviews.value = false
  }
}

// Обработчик скролла для подгрузки отзывов
const handleScroll = () => {
  const bottomOfWindow = window.innerHeight + window.scrollY >= document.documentElement.offsetHeight - 300
  if (bottomOfWindow) {
    loadReviews()
  }
}

onMounted(() => {
  // Стартуем загрузку первой порции отзывов сразу после отрисовки
  loadReviews()
  window.addEventListener('scroll', handleScroll)
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})


// --- СОСТОЯНИЕ ОПЛАТЫ И МОДАЛКИ ---
const createdOrderId = ref(null)
const isPaymentModalOpen = ref(false)
const paymentStep = ref('creating')
const paymentErrorMsg = ref('')

const getStockStatus = (count) => {
  if (count === null || count === undefined) {
    return { text: 'В наличии', color: 'text-green-600 dark:text-green-400' }
  }
  if (count > 10) {
    return { text: 'В наличии: >10 шт.', color: 'text-green-600 dark:text-green-400' }
  }
  if (count > 0) {
    return { text: `Осталось: ${count} шт.`, color: 'text-amber-600 dark:text-amber-400' }
  }
  return { text: 'Нет в наличии', color: 'text-red-500 dark:text-red-400' }
}

// Магия реактивности: проверяем URL и выбираем нужный вариант, игнорируя пустые/скрытые
watch(product, (newProduct) => {
  if (newProduct && newProduct.variants?.length > 0) {
    const availableVariants = newProduct.variants.filter(
      v => v.is_active !== false && v.items_count !== 0
    )

    if (availableVariants.length === 0) {
      selectedVariant.value = null
      return
    }

    const targetVariantId = route.query.variant
    if (targetVariantId) {
      const foundVariant = availableVariants.find(v => v.id === Number(targetVariantId))
      if (foundVariant) {
        selectedVariant.value = foundVariant
        return
      }
    }

    const sortedVariants = [...availableVariants].sort((a, b) => Number(a.price) - Number(b.price))
    selectedVariant.value = sortedVariants[0]
  }
}, { immediate: true })

// 1. ШАГ ПЕРВЫЙ: Создаем заказ
const buyProduct = async () => {
  if (!selectedVariant.value) return

  isPaymentModalOpen.value = true
  paymentStep.value = 'creating'
  paymentErrorMsg.value = ''

  try {
    const order = await $api('/api/client/orders', {
      method: 'POST',
      query: { product_variant_id: selectedVariant.value.id }
    })

    createdOrderId.value = order.id
    paymentStep.value = 'waiting'
    await waitForPaymentLink(order.id)

  } catch (error) {
    if (error.response?.status === 401) {
      isPaymentModalOpen.value = false
      toast.add({
        title: 'Требуется авторизация',
        description: 'Пожалуйста, войдите в аккаунт для оформления заказа',
        color: 'amber'
      })
    } else {
      paymentStep.value = 'error'
      paymentErrorMsg.value = error.data?.detail || 'Не удалось создать заказ. Попробуйте позже.'
    }
  }
}

// 2. ШАГ ВТОРОЙ: Ждем ссылку на оплату
const waitForPaymentLink = async (orderId) => {
  try {
    const response = await $api(`/api/client/orders/${orderId}/wait-payment`, {
      method: 'GET'
    })

    if (response) {
      paymentStep.value = 'payment_ready'
    }

  } catch (error) {
    console.error('Ошибка ожидания:', error)
    paymentStep.value = 'error'
    paymentErrorMsg.value = error.response?.status === 408
      ? 'Время ожидания истекло. Заказ сохранен, вы можете перейти к нему позже.'
      : 'Произошла ошибка при обработке заказа.'
  }
}

// 3. ШАГ ТРЕТИЙ: Эмуляция оплаты через Mock-Вебхук
const simulatePayment = async () => {
  paymentStep.value = 'processing_payment'

  try {
    await $api('/api/webhooks/payment', {
      method: 'POST',
      body: { id: createdOrderId.value }
    })

    await new Promise(resolve => setTimeout(resolve, 800))
    paymentStep.value = 'success'

  } catch (error) {
    console.error('Ошибка симуляции оплаты:', error)
    paymentStep.value = 'error'
    paymentErrorMsg.value = 'Не удалось провести оплату. Попробуйте позже.'
  }
}

useHead({
  title: computed(() => product.value ? `${product.value.title} | myMarket` : 'Загрузка товара...')
})
</script>
