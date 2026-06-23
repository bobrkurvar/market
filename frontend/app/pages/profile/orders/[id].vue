<template>
  <UContainer class="py-10">
    <div v-if="pending" class="flex justify-center py-20">
      <UIcon name="i-heroicons-arrow-path" class="w-10 h-10 animate-spin text-primary-500" />
    </div>

    <div v-else-if="order" class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div class="lg:col-span-1 space-y-6">
        <UCard :ui="{ body: { padding: 'p-6' } }">
          <template #header>
            <h3 class="font-bold text-lg text-gray-900 dark:text-white">
              Сделка #{{ order.id }}
            </h3>
          </template>

          <div class="space-y-4">
            <div>
              <p class="text-sm text-gray-500">Статус заказа</p>
              <p
                class="font-semibold"
                :class="{
                  'text-amber-600 dark:text-amber-400': order.status === 'pending_payments',
                  'text-green-600 dark:text-green-400': order.status === 'paid',
                  'text-red-600 dark:text-red-400': order.status === 'dispute' || order.status === 'canceled'
                }"
              >
                <template v-if="order.status === 'paid'">Оплачен</template>
                <template v-else-if="order.status === 'dispute'">На рассмотрении спора</template>
                <template v-else-if="order.status === 'canceled'">Отменён</template>
                <template v-else>Ожидает оплаты</template>
              </p>
            </div>

            <UDivider />

            <div>
              <p class="text-sm text-gray-500">Создан</p>
              <p class="font-medium text-gray-900 dark:text-gray-200">
                {{ new Date(order.created_at).toLocaleDateString() }}
              </p>
            </div>
          </div>
        </UCard>

        <div v-if="order.status === 'paid'" class="space-y-6">
          <UCard
            v-if="order.product_snapshot?.buyer_message"
            class="bg-blue-50 dark:bg-blue-900/20 ring-blue-200 dark:ring-blue-800"
          >
            <h3 class="text-sm font-bold text-blue-900 dark:text-blue-100 flex items-center gap-2 mb-3">
              <UIcon name="i-heroicons-information-circle" class="w-5 h-5" />
              Сообщение от продавца
            </h3>
            <p class="text-sm text-blue-800 dark:text-blue-200 whitespace-pre-line leading-relaxed">
              {{ order.product_snapshot.buyer_message }}
            </p>
          </UCard>

          <UCard v-if="order.items && order.items.length > 0">
            <template #header>
              <h3 class="text-sm font-bold text-gray-900 dark:text-white flex items-center gap-2">
                <UIcon name="i-heroicons-key" class="w-5 h-5 text-green-500" />
                Ваши покупки
              </h3>
            </template>

            <div class="space-y-3">
              <div
                v-for="item in order.items"
                :key="item.id"
                class="flex items-center gap-3 p-3 bg-gray-50 dark:bg-gray-800/50 rounded-lg border border-gray-100 dark:border-gray-700"
              >
                <code class="flex-1 font-mono text-sm font-bold text-gray-900 dark:text-white break-all">
                  {{ item.content }}
                </code>
                <UButton
                  color="gray"
                  variant="ghost"
                  icon="i-heroicons-clipboard-document"
                  size="sm"
                  @click="copyToClipboard(item.content)"
                />
              </div>
            </div>
          </UCard>


          <UCard
            v-if="!order.review"
            class="ring-amber-200 dark:ring-amber-800"
          >
            <template #header>
              <h3 class="text-sm font-bold text-gray-900 dark:text-white flex items-center gap-2">
                <UIcon name="i-heroicons-star" class="w-5 h-5 text-amber-500" />
                Оценить покупку
              </h3>
            </template>

            <div class="space-y-4">
              <p class="text-sm text-gray-600 dark:text-gray-300">
                Ваша оценка и отзыв будут показаны у купленного варианта товара.
              </p>

              <div>
                <p class="mb-2 text-sm font-medium text-gray-700 dark:text-gray-200">
                  Оценка
                </p>

                <div class="flex items-center gap-1">
                  <button
                    v-for="star in 5"
                    :key="star"
                    type="button"
                    class="rounded-md p-1 transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-primary-500"
                    :aria-label="`Поставить ${star} из 5`"
                    :disabled="isSubmittingReview"
                    @click="reviewRating = star"
                  >
                    <UIcon
                      name="i-heroicons-star-solid"
                      class="h-7 w-7"
                      :class="star <= reviewRating
                        ? 'text-amber-400'
                        : 'text-gray-300 dark:text-gray-600'"
                    />
                  </button>

                  <span
                    v-if="reviewRating"
                    class="ml-2 text-sm text-gray-500"
                  >
                    {{ reviewRating }} из 5
                  </span>
                </div>
              </div>

              <UTextarea
                v-model="reviewComment"
                :rows="3"
                :maxlength="2000"
                placeholder="Расскажите о товаре: активации, качестве, скорости выдачи..."
                :disabled="isSubmittingReview"
              />

              <UButton
                color="primary"
                icon="i-heroicons-paper-airplane"
                :loading="isSubmittingReview"
                :disabled="!reviewRating"
                @click="submitReview"
              >
                Опубликовать отзыв
              </UButton>
            </div>
          </UCard>

          <UCard
            v-else
            class="bg-green-50 dark:bg-green-900/20 ring-green-200 dark:ring-green-800"
          >
            <template #header>
              <h3 class="text-sm font-bold text-green-900 dark:text-green-100 flex items-center gap-2">
                <UIcon name="i-heroicons-check-circle" class="w-5 h-5" />
                Ваш отзыв
              </h3>
            </template>

            <div class="space-y-3">
              <div class="flex items-center gap-1">
                <UIcon
                  v-for="star in 5"
                  :key="star"
                  name="i-heroicons-star-solid"
                  class="h-6 w-6"
                  :class="star <= order.review.rating
                    ? 'text-amber-400'
                    : 'text-gray-300 dark:text-gray-600'"
                />
                <span class="ml-2 text-sm font-medium text-green-900 dark:text-green-100">
                  {{ order.review.rating }} из 5
                </span>
              </div>

              <p
                v-if="order.review.comment"
                class="text-sm text-green-800 dark:text-green-200 whitespace-pre-line leading-relaxed"
              >
                {{ order.review.comment }}
              </p>

              <p
                v-else
                class="text-sm text-green-800 dark:text-green-200"
              >
                Вы оставили оценку без комментария.
              </p>
            </div>
          </UCard>

          <UCard
            v-if="isDisputeFormOpen"
            class="ring-red-200 dark:ring-red-800"
          >
            <template #header>
              <h3 class="text-sm font-bold text-gray-900 dark:text-white">
                Открыть спор
              </h3>
            </template>

            <div class="space-y-4">
              <p class="text-sm text-gray-600 dark:text-gray-300">
                Опишите проблему. После открытия спора обычный чат и выдача ключей будут заблокированы до решения.
              </p>

              <UTextarea
                v-model="disputeReason"
                :rows="4"
                placeholder="Например: ключ не активируется, код ошибки..."
                :disabled="isDisputing"
              />

              <div class="flex gap-2">
                <UButton
                  color="red"
                  :loading="isDisputing"
                  :disabled="!disputeReason.trim()"
                  @click="openDispute"
                >
                  Открыть спор
                </UButton>

                <UButton
                  color="gray"
                  variant="ghost"
                  :disabled="isDisputing"
                  @click="closeDisputeForm"
                >
                  Отмена
                </UButton>
              </div>
            </div>
          </UCard>

          <UButton
            v-else
            color="red"
            variant="soft"
            icon="i-heroicons-shield-exclamation"
            block
            @click="isDisputeFormOpen = true"
          >
            Позвать техподдержку
          </UButton>
        </div>

        <div v-else-if="order.status === 'dispute'" class="space-y-6">
          <UCard class="bg-red-50 dark:bg-red-900/20 ring-red-200 dark:ring-red-800">
            <h3 class="text-sm font-bold text-red-900 dark:text-red-100 flex items-center gap-2 mb-2">
              <UIcon name="i-heroicons-exclamation-triangle" class="w-5 h-5" />
              Спор открыт
            </h3>
            <p class="text-sm text-red-800 dark:text-red-200 leading-relaxed">
              Сделка находится на рассмотрении. Продолжите общение в отдельном чате спора.
            </p>
          </UCard>

          <UButton
            color="red"
            icon="i-heroicons-arrow-right"
            block
            :to="disputePagePath"
          >
            Перейти к спору
          </UButton>
        </div>
      </div>

      <div class="lg:col-span-2">
        <UCard
          v-if="order.status === 'paid'"
          class="flex flex-col h-[600px] shadow-sm ring-1 ring-gray-200 dark:ring-gray-800"
          :ui="{ body: { padding: 'p-0', base: 'flex-1 overflow-hidden flex flex-col' } }"
        >
          <template #header>
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-3">
                <UIcon name="i-heroicons-chat-bubble-left-right" class="w-6 h-6 text-primary-500" />
                <h3 class="font-bold text-gray-900 dark:text-white">Чат с продавцом</h3>
              </div>

              <div
                class="flex items-center gap-2 text-sm"
                :class="isConnected ? 'text-green-600' : 'text-red-500'"
              >
                <span class="relative flex h-3 w-3">
                  <span
                    v-if="isConnected"
                    class="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"
                  />
                  <span
                    class="relative inline-flex rounded-full h-3 w-3"
                    :class="isConnected ? 'bg-green-500' : 'bg-red-500'"
                  />
                </span>
                {{ isConnected ? 'В сети' : 'Соединение...' }}
              </div>
            </div>
          </template>

          <div
            ref="chatContainer"
            class="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50 dark:bg-gray-900/30"
          >
            <div
              v-if="messages.length === 0"
              class="flex justify-center items-center h-full text-gray-400 text-sm"
            >
              Здесь пока нет сообщений. Напишите продавцу!
            </div>

            <div
              v-for="msg in messages"
              :key="msg.id"
              class="flex"
              :class="msg.sender_id === currentUser?.id ? 'justify-end' : 'justify-start'"
            >
              <div
                class="max-w-[80%] rounded-2xl px-4 py-2 shadow-sm"
                :class="msg.sender_id === currentUser?.id
                  ? 'bg-primary-500 text-white rounded-br-none'
                  : 'bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-bl-none text-gray-900 dark:text-gray-100'"
              >
                <p class="text-sm whitespace-pre-wrap leading-relaxed">{{ msg.text }}</p>
                <span
                  class="text-[10px] mt-1 block text-right"
                  :class="msg.sender_id === currentUser?.id ? 'text-primary-100' : 'text-gray-400'"
                >
                  {{ new Date(msg.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) }}
                </span>
              </div>
            </div>
          </div>

          <div class="p-4 bg-white dark:bg-gray-900 border-t border-gray-100 dark:border-gray-800">
            <form class="flex gap-2 relative" @submit.prevent="sendMessage">
              <UInput
                v-model="newMessage"
                placeholder="Введите сообщение..."
                class="flex-1"
                size="lg"
                autocomplete="off"
                :disabled="!isConnected"
              />
              <UButton
                type="submit"
                icon="i-heroicons-paper-airplane"
                color="primary"
                size="lg"
                :disabled="!newMessage.trim() || !isConnected"
              />
            </form>
          </div>
        </UCard>

        <UCard
          v-else-if="order.status === 'dispute'"
          class="h-full min-h-[360px] flex items-center justify-center"
        >
          <div class="max-w-md text-center space-y-4 py-12">
            <UIcon
              name="i-heroicons-shield-exclamation"
              class="w-14 h-14 mx-auto text-red-500"
            />
            <div>
              <h2 class="text-lg font-bold text-gray-900 dark:text-white">
                Обычный чат приостановлен
              </h2>
              <p class="mt-2 text-sm text-gray-500">
                Переписка по сделке сохранена как история. Новые сообщения отправляйте в чат спора.
              </p>
            </div>
            <UButton
              color="red"
              icon="i-heroicons-arrow-right"
              :to="disputePagePath"
            >
              Открыть чат спора
            </UButton>
          </div>
        </UCard>

        <UCard
          v-else
          class="h-full min-h-[360px] flex items-center justify-center"
        >
          <div class="max-w-md text-center space-y-3 py-12">
            <UIcon name="i-heroicons-lock-closed" class="w-12 h-12 mx-auto text-gray-400" />
            <h2 class="text-lg font-bold text-gray-900 dark:text-white">
              Чат пока недоступен
            </h2>
            <p class="text-sm text-gray-500">
              Чат станет доступен после оплаты заказа.
            </p>
          </div>
        </UCard>
      </div>
    </div>
  </UContainer>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useNuxtApp, useState, useToast } from '#imports'

const route = useRoute()
const router = useRouter()
const { $api } = useNuxtApp()
const toast = useToast()

const orderId = route.params.id
const currentUser = useState('user')

const pending = ref(true)
const order = ref(null)
const messages = ref([])

const newMessage = ref('')
const isConnected = ref(false)
const chatContainer = ref(null)
let socket = null

const isDisputing = ref(false)
const isDisputeFormOpen = ref(false)
const disputeReason = ref('')

const reviewRating = ref(0)
const reviewComment = ref('')
const isSubmittingReview = ref(false)

const disputePagePath = computed(() => `/profile/orders/${orderId}/dispute`)

const scrollToBottom = async () => {
  await nextTick()

  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight
  }
}

const copyToClipboard = async (text) => {
  try {
    await navigator.clipboard.writeText(text)
    toast.add({
      title: 'Скопировано',
      description: 'Ключ скопирован в буфер обмена',
      color: 'green'
    })
  } catch {
    toast.add({
      title: 'Ошибка',
      description: 'Не удалось скопировать текст',
      color: 'red'
    })
  }
}

const submitReview = async () => {
  if (!reviewRating.value) {
    toast.add({
      title: 'Выберите оценку',
      description: 'Поставьте от одной до пяти звёзд.',
      color: 'red'
    })
    return
  }

  isSubmittingReview.value = true

  try {
    const createdReview = await $api(`/api/client/orders/${orderId}/review`, {
      method: 'POST',
      body: {
        rating: reviewRating.value,
        comment: reviewComment.value.trim() || null
      }
    })

    order.value.review = createdReview

    toast.add({
      title: 'Отзыв опубликован',
      description: 'Спасибо, ваша оценка поможет другим покупателям.',
      color: 'green'
    })
  } catch (error) {
    const errorMsg =
      error.data?.detail ||
      error.response?._data?.detail ||
      'Не удалось опубликовать отзыв'

    toast.add({
      title: 'Ошибка',
      description: errorMsg,
      color: 'red'
    })
  } finally {
    isSubmittingReview.value = false
  }
}

const closeDisputeForm = () => {
  isDisputeFormOpen.value = false
  disputeReason.value = ''
}

const openDispute = async () => {
  const reason = disputeReason.value.trim()

  if (!reason) {
    return
  }

  isDisputing.value = true

  try {
    await $api(`/api/orders/${orderId}/dispute`, {
      method: 'POST',
      body: { reason }
    })

    toast.add({
      title: 'Спор открыт',
      description: 'Перейдите в чат спора для дальнейшего общения с поддержкой.',
      color: 'green'
    })

    await router.push(disputePagePath.value)
  } catch (error) {
    const errorMsg =
      error.data?.detail ||
      error.response?._data?.detail ||
      'Не удалось открыть спор'

    toast.add({
      title: 'Ошибка',
      description: errorMsg,
      color: 'red'
    })
  } finally {
    isDisputing.value = false
  }
}

const loadHistory = async () => {
  try {
    const historyData = await $api(`/api/orders/${orderId}/messages`)
    messages.value = historyData || []
    await scrollToBottom()
  } catch (error) {
    console.error('Ошибка обновления истории:', error)
  }
}

const connectWebSocket = () => {
  if (socket && socket.readyState !== WebSocket.CLOSED) {
    return
  }

  const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  const wsUrl = `${wsProtocol}//${window.location.host}/api/ws/orders/${orderId}/chat`

  socket = new WebSocket(wsUrl)

  socket.onopen = () => {
    isConnected.value = true
  }

  socket.onmessage = async (event) => {
    messages.value.push(JSON.parse(event.data))
    await scrollToBottom()
  }

  socket.onclose = () => {
    isConnected.value = false
    socket = null
  }
}

const disconnectWebSocket = () => {
  if (socket) {
    socket.close()
    socket = null
  }

  isConnected.value = false
}

const handleVisibilityChange = async () => {
  if (order.value?.status !== 'paid') {
    return
  }

  if (document.hidden) {
    disconnectWebSocket()
    return
  }

  await loadHistory()
  connectWebSocket()
}

onMounted(async () => {
  try {
    order.value = await $api(`/api/orders/${orderId}`)

    if (order.value.status === 'paid') {
      await loadHistory()
      connectWebSocket()
      document.addEventListener('visibilitychange', handleVisibilityChange)
    }
  } catch (error) {
    console.error('Ошибка загрузки сделки:', error)
  } finally {
    pending.value = false
  }
})

onBeforeUnmount(() => {
  disconnectWebSocket()
  document.removeEventListener('visibilitychange', handleVisibilityChange)
})

const sendMessage = () => {
  if (!newMessage.value.trim() || !socket || socket.readyState !== WebSocket.OPEN) {
    return
  }

  socket.send(newMessage.value)
  newMessage.value = ''
}
</script>
