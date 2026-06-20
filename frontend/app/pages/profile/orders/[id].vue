<template>
  <UContainer class="py-10">
    <div v-if="pending" class="flex justify-center py-20">
      <UIcon name="i-heroicons-arrow-path" class="w-10 h-10 animate-spin text-primary-500" />
    </div>

    <div v-else-if="order" class="grid grid-cols-1 lg:grid-cols-3 gap-6">

      <div class="lg:col-span-1 space-y-6">
        <UCard :ui="{ body: { padding: 'p-6' } }">
          <template #header>
            <h3 class="font-bold text-lg text-gray-900 dark:text-white">Сделка #{{ order.id }}</h3>
          </template>

          <div class="space-y-4">
            <div>
              <p class="text-sm text-gray-500">Статус заказа</p>
              <p class="font-semibold text-amber-600 dark:text-amber-400">Ожидает выдачи товара</p>
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
      </div>

      <div class="lg:col-span-2">
        <UCard class="flex flex-col h-[600px] shadow-sm ring-1 ring-gray-200 dark:ring-gray-800"
               :ui="{ body: { padding: 'p-0', base: 'flex-1 overflow-hidden flex flex-col' } }">

          <template #header>
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-3">
                <UIcon name="i-heroicons-chat-bubble-left-right" class="w-6 h-6 text-primary-500" />
                <h3 class="font-bold text-gray-900 dark:text-white">Чат с продавцом</h3>
              </div>
              <div class="flex items-center gap-2 text-sm" :class="isConnected ? 'text-green-600' : 'text-red-500'">
                <span class="relative flex h-3 w-3">
                  <span v-if="isConnected" class="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                  <span class="relative inline-flex rounded-full h-3 w-3" :class="isConnected ? 'bg-green-500' : 'bg-red-500'"></span>
                </span>
                {{ isConnected ? 'В сети' : 'Соединение...' }}
              </div>
            </div>
          </template>

          <div ref="chatContainer" class="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50 dark:bg-gray-900/30">

            <div v-if="messages.length === 0" class="flex justify-center items-center h-full text-gray-400 text-sm">
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
                <span class="text-[10px] mt-1 block text-right"
                      :class="msg.sender_id === currentUser?.id ? 'text-primary-100' : 'text-gray-400'">
                  {{ new Date(msg.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) }}
                </span>
              </div>
            </div>
          </div>

          <div class="p-4 bg-white dark:bg-gray-900 border-t border-gray-100 dark:border-gray-800">
            <form @submit.prevent="sendMessage" class="flex gap-2 relative">
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
      </div>

    </div>
  </UContainer>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { useNuxtApp, useState } from '#imports'

const route = useRoute()
const { $api } = useNuxtApp()
const orderId = route.params.id
const currentUser = useState('user')

const pending = ref(true)
const order = ref(null)
const messages = ref([])

const newMessage = ref('')
const isConnected = ref(false)
const chatContainer = ref(null)
let socket = null

const scrollToBottom = async () => {
  await nextTick()
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight
  }
}

// 1. ВЫНОСИМ ЗАГРУЗКУ ИСТОРИИ В ОТДЕЛЬНУЮ ФУНКЦИЮ
const loadHistory = async () => {
  try {
    const historyData = await $api(`/api/orders/${orderId}/messages`)
    messages.value = historyData || []
    scrollToBottom()
  } catch (e) {
    console.error("Ошибка обновления истории:", e)
  }
}

// 2. ВЫНОСИМ ЛОГИКУ ПОДКЛЮЧЕНИЯ ВЕБСОКЕТА
const connectWebSocket = () => {
  if (socket && socket.readyState !== WebSocket.CLOSED) return

  const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const wsUrl = `${wsProtocol}//${window.location.host}/api/ws/orders/${orderId}/chat`;

  socket = new WebSocket(wsUrl);

  socket.onopen = () => {
    isConnected.value = true
  }

  socket.onmessage = (event) => {
    const incomingMsg = JSON.parse(event.data)
    messages.value.push(incomingMsg)
    scrollToBottom()
  }

  socket.onclose = () => {
    isConnected.value = false
  }
}

// 3. ВЫНОСИМ ЛОГИКУ ОТКЛЮЧЕНИЯ
const disconnectWebSocket = () => {
  if (socket) {
    socket.close()
    socket = null
    isConnected.value = false
  }
}

// 4. ОБРАБОТЧИК ВИДИМОСТИ СТРАНИЦЫ (МАГИЯ ЗДЕСЬ)
const handleVisibilityChange = async () => {
  if (document.hidden) {
    // Пользователь ушел на другую вкладку - отключаем сокет
    disconnectWebSocket()
  } else {
    // Пользователь вернулся!
    // Сначала подтягиваем пропущенные сообщения по REST
    await loadHistory()
    // Затем заново открываем сокет
    connectWebSocket()
  }
}

onMounted(async () => {
  try {
    // Первичная загрузка сделки
    order.value = await $api(`/api/orders/${orderId}`)
    await loadHistory()
    pending.value = false

    // Подключаем сокет
    connectWebSocket()

    // Подписываемся на событие сворачивания/разворачивания вкладки
    document.addEventListener('visibilitychange', handleVisibilityChange)

  } catch (error) {
    console.error('Ошибка загрузки сделки:', error)
    pending.value = false
  }
})

onBeforeUnmount(() => {
  disconnectWebSocket()
  document.removeEventListener('visibilitychange', handleVisibilityChange)
})

const sendMessage = () => {
  if (!newMessage.value.trim() || !socket || socket.readyState !== WebSocket.OPEN) return
  socket.send(newMessage.value)
  newMessage.value = ''
}
</script>
