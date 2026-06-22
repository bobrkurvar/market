<template>
  <UContainer class="py-10">
    <div v-if="pending" class="flex justify-center py-20">
      <UIcon name="i-heroicons-arrow-path" class="w-10 h-10 animate-spin text-primary-500" />
    </div>

    <div v-else-if="dispute" class="mx-auto max-w-5xl space-y-6">
      <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div class="flex items-start gap-3">
          <UButton
            color="gray"
            variant="ghost"
            icon="i-heroicons-arrow-left"
            :to="orderPagePath"
            aria-label="Вернуться к заказу"
          />
          <div>
            <div class="flex flex-wrap items-center gap-3">
              <h1 class="text-2xl font-bold text-gray-900 dark:text-white">
                Спор по сделке #{{ dispute.order_id }}
              </h1>
              <UBadge :color="dispute.status === 'open' ? 'red' : 'gray'" variant="soft">
                {{ dispute.status === 'open' ? 'На рассмотрении' : 'Решён' }}
              </UBadge>
            </div>
            <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
              Открыт {{ formatDate(dispute.created_at) }}
            </p>
          </div>
        </div>

        <UButton
          color="gray"
          variant="soft"
          icon="i-heroicons-chat-bubble-left-right"
          :to="orderPagePath"
        >
          История сделки
        </UButton>
      </div>

      <UCard class="ring-red-200 dark:ring-red-800">
        <template #header>
          <div class="flex items-center gap-2">
            <UIcon name="i-heroicons-shield-exclamation" class="h-5 w-5 text-red-500" />
            <h2 class="font-bold text-gray-900 dark:text-white">Причина спора</h2>
          </div>
        </template>

        <p class="whitespace-pre-wrap text-sm leading-relaxed text-gray-700 dark:text-gray-200">
          {{ dispute.reason }}
        </p>

        <div v-if="dispute.status === 'resolved'" class="mt-5 rounded-xl bg-gray-50 p-4 dark:bg-gray-800/70">
          <p class="text-xs font-semibold uppercase tracking-wide text-gray-500">Решение поддержки</p>
          <p class="mt-2 whitespace-pre-wrap text-sm leading-relaxed text-gray-800 dark:text-gray-100">
            {{ dispute.resolution || 'Решение не указано.' }}
          </p>
          <p v-if="dispute.resolved_at" class="mt-2 text-xs text-gray-500">
            Закрыт {{ formatDate(dispute.resolved_at) }}
          </p>
        </div>
      </UCard>

      <UCard
        class="flex h-[600px] flex-col shadow-sm ring-1 ring-gray-200 dark:ring-gray-800"
        :ui="{ body: { padding: 'p-0', base: 'flex-1 overflow-hidden flex flex-col' } }"
      >
        <template #header>
          <div class="flex items-center justify-between gap-4">
            <div class="flex items-center gap-3">
              <UIcon name="i-heroicons-chat-bubble-left-right" class="h-6 w-6 text-red-500" />
              <div>
                <h2 class="font-bold text-gray-900 dark:text-white">Чат спора</h2>
                <p class="text-xs text-gray-500 dark:text-gray-400">Покупатель, продавец и поддержка</p>
              </div>
            </div>

            <div
              v-if="dispute.status === 'open'"
              class="flex items-center gap-2 text-sm"
              :class="isConnected ? 'text-green-600' : 'text-red-500'"
            >
              <span class="relative flex h-3 w-3">
                <span
                  v-if="isConnected"
                  class="absolute inline-flex h-full w-full animate-ping rounded-full bg-green-400 opacity-75"
                />
                <span
                  class="relative inline-flex h-3 w-3 rounded-full"
                  :class="isConnected ? 'bg-green-500' : 'bg-red-500'"
                />
              </span>
              {{ isConnected ? 'В сети' : 'Соединение...' }}
            </div>

            <UBadge v-else color="gray" variant="soft">Чат закрыт</UBadge>
          </div>
        </template>

        <div
          ref="chatContainer"
          class="flex-1 space-y-4 overflow-y-auto bg-gray-50 p-4 dark:bg-gray-900/30"
        >
          <div
            v-if="messages.length === 0"
            class="flex h-full items-center justify-center text-center text-sm text-gray-400"
          >
            В чате спора пока нет сообщений. Опишите обстоятельства и дождитесь ответа поддержки.
          </div>

          <div
            v-for="message in messages"
            :key="message.id"
            class="flex"
            :class="isOwnMessage(message) ? 'justify-end' : 'justify-start'"
          >
            <div
              class="max-w-[80%] rounded-2xl px-4 py-2 shadow-sm"
              :class="isOwnMessage(message)
                ? 'rounded-br-none bg-primary-500 text-white'
                : 'rounded-bl-none border border-gray-200 bg-white text-gray-900 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-100'"
            >
              <p v-if="!isOwnMessage(message)" class="mb-1 text-xs font-semibold text-gray-500 dark:text-gray-400">
                {{ authorLabel(message) }}
              </p>
              <p class="whitespace-pre-wrap text-sm leading-relaxed">{{ message.text }}</p>
              <span
                class="mt-1 block text-right text-[10px]"
                :class="isOwnMessage(message) ? 'text-primary-100' : 'text-gray-400'"
              >
                {{ formatTime(message.created_at) }}
              </span>
            </div>
          </div>
        </div>

        <div v-if="dispute.status === 'open'" class="border-t border-gray-100 bg-white p-4 dark:border-gray-800 dark:bg-gray-900">
          <form class="flex gap-2" @submit.prevent="sendMessage">
            <UInput
              v-model="newMessage"
              class="flex-1"
              size="lg"
              autocomplete="off"
              placeholder="Введите сообщение в чат спора..."
              :disabled="!isConnected"
            />
            <UButton
              type="submit"
              icon="i-heroicons-paper-airplane"
              color="red"
              size="lg"
              :disabled="!newMessage.trim() || !isConnected"
            />
          </form>
        </div>
      </UCard>
    </div>

    <UCard v-else class="mx-auto max-w-xl text-center">
      <div class="space-y-4 py-8">
        <UIcon name="i-heroicons-exclamation-triangle" class="mx-auto h-12 w-12 text-red-500" />
        <div>
          <h1 class="text-xl font-bold text-gray-900 dark:text-white">Не удалось открыть спор</h1>
          <p class="mt-2 text-sm text-gray-500">Спор не найден или у вас нет к нему доступа.</p>
        </div>
        <UButton color="gray" :to="orderPagePath">Вернуться к сделке</UButton>
      </div>
    </UCard>
  </UContainer>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useNuxtApp, useState, useToast } from '#imports'

definePageMeta({
  path: '/profile/orders/:id/dispute',
})

const route = useRoute()
const { $api } = useNuxtApp()
const toast = useToast()

const orderId = computed(() => String(route.params.id))
const orderPagePath = computed(() => `/profile/orders/${orderId.value}`)
const currentUser = useState('user')

const pending = ref(true)
const dispute = ref(null)
const messages = ref([])
const newMessage = ref('')
const isConnected = ref(false)
const chatContainer = ref(null)

let socket = null

const isOwnMessage = (message) => (
  String(message.sender_id) === String(currentUser.value?.id)
)

const authorLabel = (message) => {
  if (String(message.sender_id) === String(dispute.value?.opened_by_id)) {
    return 'Участник, открывший спор'
  }

  return 'Участник спора или поддержка'
}

const formatDate = (date) => new Date(date).toLocaleString('ru-RU', {
  day: '2-digit',
  month: '2-digit',
  year: 'numeric',
  hour: '2-digit',
  minute: '2-digit',
})

const formatTime = (date) => new Date(date).toLocaleTimeString('ru-RU', {
  hour: '2-digit',
  minute: '2-digit',
})

const scrollToBottom = async () => {
  await nextTick()

  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight
  }
}

const loadHistory = async () => {
  const history = await $api(
    `/api/orders/${orderId.value}/dispute/messages`,
  )

  messages.value = history || []
  await scrollToBottom()
}

const disconnectSocket = () => {
  if (socket) {
    socket.close()
    socket = null
  }

  isConnected.value = false
}

const connectSocket = () => {
  if (!dispute.value || dispute.value.status !== 'open') {
    return
  }

  if (socket && socket.readyState !== WebSocket.CLOSED) {
    return
  }

  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'

  const wsUrl = (
    `${protocol}//${window.location.host}` +
    `/api/ws/disputes/${dispute.value.id}/chat`
  )

  socket = new WebSocket(wsUrl)

  socket.onopen = () => {
    isConnected.value = true
  }

  socket.onmessage = async (event) => {
    const message = JSON.parse(event.data)

    const alreadyExists = messages.value.some(
      (item) => item.id === message.id,
    )

    if (!alreadyExists) {
      messages.value.push(message)
      await scrollToBottom()
    }
  }

  socket.onclose = () => {
    isConnected.value = false
    socket = null
  }

  socket.onerror = () => {
    toast.add({
      title: 'Ошибка',
      description: 'Не удалось подключиться к чату спора',
      color: 'red',
    })
  }
}

const sendMessage = () => {
  const text = newMessage.value.trim()

  if (!text || !socket || socket.readyState !== WebSocket.OPEN) {
    return
  }

  socket.send(text)
  newMessage.value = ''
}

onMounted(async () => {
  try {
    dispute.value = await $api(
      `/api/orders/${orderId.value}/dispute`,
    )

    await loadHistory()
    connectSocket()
  } catch (error) {
    console.error('Не удалось загрузить спор:', error)

    toast.add({
      title: 'Ошибка',
      description: 'Не удалось загрузить данные спора',
      color: 'red',
    })
  } finally {
    pending.value = false
  }
})

onBeforeUnmount(() => {
  disconnectSocket()
})

useHead({
  title: 'Спор по заказу | myMarket',
})
</script>
