<template>
  <div class="min-h-screen bg-gray-50 font-sans text-gray-900">
    <main class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">

      <div class="flex items-center space-x-8 border-b border-gray-200 mb-8 overflow-x-auto">
        <button
          @click="activeTab = 'dashboard'"
          :class="['pb-3 font-medium text-lg transition-colors border-b-2 whitespace-nowrap', activeTab === 'dashboard' ? 'border-indigo-600 text-indigo-600' : 'border-transparent text-gray-500 hover:text-gray-700']"
        >
          Главная панель
        </button>
        <button
          @click="activeTab = 'categories'"
          :class="['pb-3 font-medium text-lg transition-colors border-b-2 whitespace-nowrap', activeTab === 'categories' ? 'border-indigo-600 text-indigo-600' : 'border-transparent text-gray-500 hover:text-gray-700']"
        >
          Категории
        </button>
        <button
          @click="activeTab = 'disputes'"
          :class="['pb-3 font-medium text-lg transition-colors border-b-2 flex items-center whitespace-nowrap', activeTab === 'disputes' ? 'border-indigo-600 text-indigo-600' : 'border-transparent text-gray-500 hover:text-gray-700']"
        >
          Арбитраж
          <span v-if="disputes.length" :class="['ml-2 text-xs px-2 py-0.5 rounded-full', activeTab === 'disputes' ? 'bg-indigo-100 text-indigo-600' : 'bg-gray-200 text-gray-600']">
            {{ disputes.length }}
          </span>
        </button>
        <button
          @click="activeTab = 'products'"
          :class="['pb-3 font-medium text-lg transition-colors border-b-2 whitespace-nowrap', activeTab === 'products' ? 'border-indigo-600 text-indigo-600' : 'border-transparent text-gray-500 hover:text-gray-700']"
        >
          Модерация
        </button>
      </div>

      <div v-if="activeTab === 'dashboard'" class="space-y-6 animate-fadeIn">
        <h1 class="text-2xl font-bold text-gray-900 mb-6">Обзор платформы</h1>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div class="bg-white p-6 rounded-xl border shadow-sm flex items-center justify-between">
            <div>
              <div class="text-sm text-gray-500 mb-1">Оборот платформы</div>
              <div class="text-3xl font-bold text-gray-900">1 245 000 ₽</div>
            </div>
            <div class="bg-green-100 p-4 rounded-full text-green-600">
              <UIcon name="i-heroicons-banknotes" class="w-8 h-8" />
            </div>
          </div>

          <div class="bg-white p-6 rounded-xl border shadow-sm flex items-center justify-between">
            <div>
              <div class="text-sm text-gray-500 mb-1">Активных продавцов</div>
              <div class="text-3xl font-bold text-gray-900">342</div>
            </div>
            <div class="bg-indigo-100 p-4 rounded-full text-indigo-600">
              <UIcon name="i-heroicons-users" class="w-8 h-8" />
            </div>
          </div>
        </div>
      </div>

      <div v-else-if="activeTab === 'categories'">
        <div v-if="categoryView === 'list'" class="space-y-6 animate-fadeIn">
          <div class="flex justify-between items-center">
            <h1 class="text-2xl font-bold text-gray-900">Дерево категорий</h1>
            <button
              @click="openCategoryForm(null)"
              class="bg-indigo-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-indigo-700 transition shadow-sm"
            >
              + Создать корень
            </button>
          </div>

          <div class="bg-white rounded-xl border shadow-sm overflow-hidden">
            <div v-if="categoriesPending" class="p-12 flex justify-center">
              <UIcon name="i-heroicons-arrow-path" class="animate-spin w-8 h-8 text-indigo-500" />
            </div>
            <div v-else-if="categories.length === 0" class="p-12 text-center text-gray-500">
              Каталог пуст. Создайте первую категорию, чтобы начать.
            </div>
            <div v-else class="divide-y">
              <div
                v-for="cat in categories"
                :key="cat.id"
                class="flex items-center justify-between p-4 hover:bg-gray-50 transition group"
                :style="{ paddingLeft: `${cat.level * 32 + 16}px` }"
              >
                <div class="flex items-center space-x-3">
                  <div class="w-8 h-8 flex-shrink-0 flex items-center justify-center bg-gray-100 rounded border overflow-hidden">
                     <img v-if="cat.search_url" :src="cat.search_url" :alt="cat.name" class="w-full h-full object-contain p-1" />
                     <UIcon v-else :name="cat.has_children ? 'i-heroicons-folder-open' : 'i-heroicons-document-text'" :class="cat.has_children ? 'text-indigo-500 w-5 h-5' : 'text-gray-400 w-4 h-4'" />
                  </div>
                  <span :class="['font-medium', cat.level === 0 ? 'text-gray-900' : 'text-gray-600']">{{ cat.name }}</span>
                </div>
                <div class="flex space-x-2 opacity-0 group-hover:opacity-100 transition">
                  <button @click="openCategoryForm(cat)" class="text-indigo-600 hover:bg-indigo-50 p-1.5 rounded" title="Добавить подкатегорию">
                    <UIcon name="i-heroicons-plus" class="w-5 h-5" />
                  </button>
                  <button @click="confirmDelete(cat)" class="text-red-500 hover:bg-red-50 p-1.5 rounded" title="Удалить">
                    <UIcon name="i-heroicons-trash" class="w-5 h-5" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div v-else-if="categoryView === 'create'" class="max-w-4xl mx-auto animate-fadeIn">
          <button
            @click="categoryView = 'list'"
            class="flex items-center text-gray-500 hover:text-gray-900 mb-6 font-medium transition"
          >
            <span class="mr-2">←</span> Назад к списку
          </button>

          <div class="bg-white p-8 rounded-xl border shadow-sm">
            <h2 class="text-2xl font-bold mb-8 text-gray-900">
              {{ categoryForm.parent_id ? `Новая подкатегория для «${categoryForm.parent_name}»` : 'Новый корневой раздел' }}
            </h2>

            <form @submit.prevent="submitCategory" class="space-y-8">
              <section>
                <div class="space-y-4">
                  <div>
                    <label class="block text-sm font-medium mb-1">Название категории <span class="text-red-500">*</span></label>
                    <input v-model="categoryForm.name" type="text" required placeholder="Например: Ключи Steam" class="w-full border border-gray-300 rounded-lg p-3 focus:ring-2 focus:ring-indigo-500 focus:outline-none" />
                  </div>

                  <div>
                    <label class="block text-sm font-medium mb-1">Иконка категории</label>
                    <input
                      type="file"
                      accept="image/*"
                      @change="handleFileChange"
                      class="w-full border border-gray-300 rounded-lg p-3 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100"
                    />
                  </div>
                </div>
              </section>

              <section>
                <div class="flex justify-between items-center mb-4 border-b pb-2">
                  <h3 class="text-lg font-semibold">Системные свойства и фильтры</h3>
                  <button type="button" @click="addFilter" class="text-indigo-600 hover:underline text-sm font-medium flex items-center">
                    <span>+ Добавить свойство</span>
                  </button>
                </div>

                <div class="space-y-4">
                  <div v-for="(filter, index) in categoryForm.filter_config" :key="index" class="bg-gray-50 p-4 rounded-lg border relative group">
                    <button type="button" @click="removeFilter(index)" class="absolute top-4 right-4 text-gray-400 hover:text-red-500 transition opacity-0 group-hover:opacity-100" title="Удалить">
                      ✕
                    </button>

                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4 pr-6">
                      <div>
                        <label class="block text-xs font-medium text-gray-600 mb-1">Название (Label) <span class="text-red-500">*</span></label>
                        <input v-model="filter.label" type="text" required placeholder="Напр: Платформа" class="w-full border border-gray-300 rounded p-2 text-sm focus:ring-2 focus:ring-indigo-500 focus:outline-none" />
                      </div>
                      <div>
                        <label class="block text-xs font-medium text-gray-600 mb-1">Системный ключ (Key) <span class="text-red-500">*</span></label>
                        <input v-model="filter.key" type="text" required placeholder="Напр: platform" class="w-full border border-gray-300 rounded p-2 text-sm focus:ring-2 focus:ring-indigo-500 focus:outline-none" />
                      </div>
                    </div>

                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 items-end">
                      <div>
                        <label class="block text-xs font-medium text-gray-600 mb-1">Тип (UI) <span class="text-red-500">*</span></label>
                        <select v-model="filter.type" required class="w-full border border-gray-300 rounded p-2 text-sm bg-white focus:ring-2 focus:ring-indigo-500 focus:outline-none">
                          <option value="select">Выпадающий список</option>
                          <option value="checkbox">Множественный выбор</option>
                          <option value="radio">Одиночный выбор</option>
                        </select>
                      </div>
                      <div class="pb-1">
                        <label class="flex items-center space-x-2 cursor-pointer">
                          <input type="checkbox" v-model="filter.strict_options" class="text-indigo-600 focus:ring-indigo-500 rounded-sm">
                          <span class="text-sm font-medium text-gray-700">Строгая валидация</span>
                        </label>
                      </div>
                    </div>

                    <div class="mt-4">
                      <label class="block text-xs font-medium text-gray-600 mb-1">Варианты (через запятую)</label>
                      <input v-model="filter.optionsText" type="text" placeholder="Напр: Steam, Epic Games, Origin" class="w-full border border-gray-300 rounded p-2 text-sm focus:ring-2 focus:ring-indigo-500 focus:outline-none" />
                    </div>
                  </div>
                </div>
              </section>

              <div class="flex justify-end pt-6 border-t mt-8">
                <button type="submit" :disabled="isSubmittingCategory" class="bg-indigo-600 text-white px-8 py-3 rounded-lg font-medium hover:bg-indigo-700 transition shadow-md disabled:opacity-50">
                  {{ isSubmittingCategory ? 'Сохранение...' : 'Создать категорию' }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>

      <div v-else-if="activeTab === 'disputes'">
        <div v-if="disputeView === 'list'" class="space-y-6 animate-fadeIn">
          <div class="flex justify-between items-center">
            <div>
              <h1 class="text-2xl font-bold text-gray-900">Арбитраж и споры</h1>
              <p class="text-sm text-gray-500 mt-1">Открывайте карточку спора, чтобы увидеть чат разбирательства и исходную переписку по заказу.</p>
            </div>
            <button @click="fetchDisputes" class="text-indigo-600 hover:text-indigo-800 text-sm font-medium flex items-center">
              <UIcon name="i-heroicons-arrow-path" class="w-5 h-5 mr-1" /> Обновить
            </button>
          </div>

          <div class="bg-white rounded-xl border shadow-sm overflow-hidden">
            <div v-if="disputesPending" class="p-12 flex justify-center">
              <UIcon name="i-heroicons-arrow-path" class="animate-spin w-8 h-8 text-indigo-500" />
            </div>

            <div v-else-if="disputes.length === 0" class="p-12 text-center text-gray-500">
              <UIcon name="i-heroicons-check-badge" class="w-16 h-16 mx-auto text-gray-300 mb-3" />
              Споров пока нет.
            </div>

            <div v-else class="overflow-x-auto">
              <table class="w-full min-w-[850px] text-left border-collapse">
                <thead>
                  <tr class="bg-gray-50 border-b text-sm text-gray-500">
                    <th class="p-4 font-medium">Спор</th>
                    <th class="p-4 font-medium">Заказ</th>
                    <th class="p-4 font-medium">Причина</th>
                    <th class="p-4 font-medium">Открыл</th>
                    <th class="p-4 font-medium">Статус</th>
                    <th class="p-4 font-medium">Дата</th>
                    <th class="p-4 font-medium text-right">Действие</th>
                  </tr>
                </thead>
                <tbody class="divide-y">
                  <tr v-for="dispute in disputes" :key="dispute.id" class="hover:bg-gray-50 transition">
                    <td class="p-4 font-medium text-gray-900">#{{ dispute.id }}</td>
                    <td class="p-4 text-gray-700">#{{ dispute.order_id }}</td>
                    <td class="p-4 text-gray-700 max-w-xs">
                      <p class="line-clamp-2">{{ dispute.reason }}</p>
                    </td>
                    <td class="p-4 text-gray-600">Пользователь #{{ dispute.opened_by_id }}</td>
                    <td class="p-4">
                      <span
                        class="inline-flex px-2.5 py-1 rounded-full text-xs font-semibold"
                        :class="disputeStatusClass(dispute.status)"
                      >
                        {{ disputeStatusLabel(dispute.status) }}
                      </span>
                    </td>
                    <td class="p-4 text-gray-600">{{ formatDate(dispute.created_at) }}</td>
                    <td class="p-4 text-right">
                      <button
                        @click="openDispute(dispute)"
                        class="inline-flex items-center px-4 py-2 bg-indigo-50 text-indigo-700 text-sm font-medium rounded-lg hover:bg-indigo-100 transition"
                      >
                        Открыть
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <div v-else-if="disputeView === 'detail' && activeDispute" class="max-w-7xl mx-auto animate-fadeIn">
          <button
            @click="closeDispute"
            class="flex items-center text-gray-500 hover:text-gray-900 mb-6 font-medium transition"
          >
            <span class="mr-2">←</span> Назад к списку споров
          </button>

          <section class="bg-white rounded-xl border shadow-sm p-6 mb-6">
            <div class="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
              <div>
                <div class="flex items-center gap-3 flex-wrap">
                  <h2 class="text-2xl font-bold text-gray-900">
                    Спор #{{ activeDispute.id }}
                  </h2>
                  <span
                    class="inline-flex px-2.5 py-1 rounded-full text-xs font-semibold"
                    :class="disputeStatusClass(activeDispute.status)"
                  >
                    {{ disputeStatusLabel(activeDispute.status) }}
                  </span>
                </div>
                <p class="text-sm text-gray-500 mt-1">
                  Заказ #{{ activeDispute.order_id }} · открыт {{ formatDate(activeDispute.created_at) }} пользователем #{{ activeDispute.opened_by_id }}
                </p>
              </div>
              <button
                @click="reloadDisputeChats"
                :disabled="chatPending"
                class="inline-flex items-center justify-center px-4 py-2 text-sm font-medium text-indigo-700 bg-indigo-50 rounded-lg hover:bg-indigo-100 transition disabled:opacity-50"
              >
                <UIcon name="i-heroicons-arrow-path" :class="['w-5 h-5 mr-1', chatPending ? 'animate-spin' : '']" />
                Обновить
              </button>
            </div>

            <div class="mt-5 rounded-lg border border-amber-200 bg-amber-50 p-4">
              <p class="text-xs font-semibold uppercase tracking-wide text-amber-700 mb-1">Причина спора</p>
              <p class="text-sm text-amber-950 whitespace-pre-wrap">{{ activeDispute.reason }}</p>
            </div>

            <div v-if="activeDispute.resolution" class="mt-4 rounded-lg border border-green-200 bg-green-50 p-4">
              <p class="text-xs font-semibold uppercase tracking-wide text-green-700 mb-1">Решение</p>
              <p class="text-sm text-green-950 whitespace-pre-wrap">{{ activeDispute.resolution }}</p>
              <p v-if="activeDispute.resolved_at" class="text-xs text-green-700 mt-2">
                Закрыт: {{ formatDate(activeDispute.resolved_at) }}
              </p>
            </div>
          </section>

          <div class="grid grid-cols-1 xl:grid-cols-2 gap-6">
            <section class="bg-white rounded-xl border shadow-sm flex flex-col h-[68vh] min-h-[520px]">
              <div class="p-5 border-b bg-indigo-50/60 rounded-t-xl">
                <div class="flex items-center justify-between gap-4">
                  <div>
                    <h3 class="text-lg font-bold text-gray-900">Чат разбирательства</h3>
                    <p class="text-sm text-gray-500 mt-1">Покупатель, продавец и поддержка.</p>
                  </div>
                  <span
                    class="text-xs font-medium px-2 py-1 rounded-full"
                    :class="isDisputeSocketConnected ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600'"
                  >
                    {{ isDisputeSocketConnected ? 'Онлайн' : 'Не подключён' }}
                  </span>
                </div>
              </div>

              <div class="flex-1 overflow-y-auto p-5 space-y-4 bg-gray-50/50">
                <div v-if="chatPending" class="flex justify-center py-10">
                  <UIcon name="i-heroicons-arrow-path" class="animate-spin w-8 h-8 text-indigo-500" />
                </div>

                <div v-else-if="activeDisputeMessages.length === 0" class="text-center text-gray-400 mt-10 italic">
                  В чате спора пока нет сообщений.
                </div>

                <div
                  v-for="msg in activeDisputeMessages"
                  :key="msg.id"
                  class="flex flex-col"
                  :class="isOwnMessage(msg) ? 'items-end' : 'items-start'"
                >
                  <span class="text-xs text-gray-500 mb-1 px-1 font-medium">
                    {{ messageAuthorLabel(msg) }} · {{ formatDate(msg.created_at, true) }}
                  </span>
                  <div
                    class="max-w-[85%] rounded-2xl px-4 py-3 shadow-sm text-sm"
                    :class="isOwnMessage(msg)
                      ? 'bg-indigo-600 text-white rounded-br-none'
                      : 'bg-white border border-gray-200 text-gray-800 rounded-bl-none'"
                  >
                    <p class="whitespace-pre-wrap leading-relaxed">{{ msg.text }}</p>
                  </div>
                </div>
              </div>

              <form
                v-if="activeDispute.status === 'open'"
                @submit.prevent="sendDisputeMessage"
                class="p-4 border-t bg-white rounded-b-xl"
              >
                <textarea
                  v-model="newDisputeMessage"
                  rows="3"
                  placeholder="Напишите сообщение от имени поддержки…"
                  class="w-full resize-none border border-gray-300 rounded-lg p-3 text-sm focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                  @keydown.enter.exact.prevent="sendDisputeMessage"
                />
                <div class="flex items-center justify-between mt-3">
                  <p class="text-xs text-gray-500">Enter — отправить, Shift + Enter — новая строка.</p>
                  <button
                    type="submit"
                    :disabled="!newDisputeMessage.trim() || !isDisputeSocketConnected"
                    class="inline-flex items-center px-4 py-2 bg-indigo-600 text-white text-sm font-medium rounded-lg hover:bg-indigo-700 transition disabled:opacity-50"
                  >
                    <UIcon name="i-heroicons-paper-airplane" class="w-4 h-4 mr-1.5" />
                    Отправить
                  </button>
                </div>
              </form>

              <div v-else class="p-4 border-t bg-gray-50 rounded-b-xl text-sm text-gray-500">
                Спор закрыт: новые сообщения отправлять нельзя.
              </div>
            </section>

            <section class="bg-white rounded-xl border shadow-sm flex flex-col h-[68vh] min-h-[520px]">
              <div class="p-5 border-b bg-gray-50 rounded-t-xl">
                <h3 class="text-lg font-bold text-gray-900">Исходный чат заказа</h3>
                <p class="text-sm text-gray-500 mt-1">Только для чтения: история сделки до и во время разбирательства.</p>
              </div>

              <div class="flex-1 overflow-y-auto p-5 space-y-4 bg-gray-50/50">
                <div v-if="chatPending" class="flex justify-center py-10">
                  <UIcon name="i-heroicons-arrow-path" class="animate-spin w-8 h-8 text-indigo-500" />
                </div>

                <div v-else-if="activeOrderMessages.length === 0" class="text-center text-gray-400 mt-10 italic">
                  В исходном чате заказа нет сообщений.
                </div>

                <div
                  v-for="msg in activeOrderMessages"
                  :key="msg.id"
                  class="flex flex-col items-start"
                >
                  <span class="text-xs text-gray-500 mb-1 px-1 font-medium">
                    Пользователь #{{ msg.sender_id }} · {{ formatDate(msg.created_at, true) }}
                  </span>
                  <div class="max-w-[85%] rounded-2xl rounded-bl-none px-4 py-3 border border-gray-200 bg-white text-sm text-gray-800 shadow-sm">
                    <p class="whitespace-pre-wrap leading-relaxed">{{ msg.text }}</p>
                  </div>
                </div>
              </div>
            </section>
          </div>
        </div>
      </div>

      <div v-else-if="activeTab === 'products'" class="space-y-6 animate-fadeIn">
        <h1 class="text-2xl font-bold text-gray-900 mb-6">Модерация товаров</h1>
        <div class="bg-white rounded-xl border border-dashed border-gray-300 p-12 text-center text-gray-500 shadow-sm">
          <UIcon name="i-heroicons-shield-check" class="w-16 h-16 mx-auto text-gray-300 mb-3" />
          <p class="font-medium">Все товары проверены. Нарушений не найдено.</p>
        </div>
      </div>

    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'

definePageMeta({
  middleware: [
    async function () {
      const currentUser = useState('user')
      const { $api } = useNuxtApp()

      if (!currentUser.value) {
        try {
          const res = await $api('/api/me')
          currentUser.value = res?.user || res
        } catch {
          currentUser.value = null
        }
      }

      if (currentUser.value?.role !== 'admin') {
        return navigateTo('/')
      }
    }
  ]
})

const toast = useToast()
const { $api } = useNuxtApp()

// Состояния вкладок и видов
const activeTab = ref('dashboard')
const categoryView = ref('list') // 'list' | 'create'

// --- КАТЕГОРИИ ---
const categories = ref([])
const categoriesPending = ref(false)
const isSubmittingCategory = ref(false)
const categoryForm = ref({
  name: '', parent_id: null, parent_name: '', file: null, filter_config: []
})

const fetchCategories = async () => {
  categoriesPending.value = true
  try {
    categories.value = await $api('/api/admin/categories')
  } catch (error) {
    toast.add({ title: 'Ошибка', description: 'Не удалось загрузить категории', color: 'red' })
  } finally {
    categoriesPending.value = false
  }
}

const openCategoryForm = (parentCategory = null) => {
  categoryForm.value = {
    name: '',
    parent_id: parentCategory ? parentCategory.id : null,
    parent_name: parentCategory ? parentCategory.name : '',
    file: null,
    filter_config: []
  }
  categoryView.value = 'create'
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const handleFileChange = (event) => {
  categoryForm.value.file = event.target.files?.[0] || null
}

const addFilter = () => {
  categoryForm.value.filter_config.push({ label: '', key: '', type: 'select', strict_options: true, optionsText: '' })
}
const removeFilter = (index) => categoryForm.value.filter_config.splice(index, 1)

const submitCategory = async () => {
  if (!categoryForm.value.name.trim()) return
  isSubmittingCategory.value = true

  try {
    const categoryData = {
      name: categoryForm.value.name,
      parent_id: categoryForm.value.parent_id || null,
      filter_config: categoryForm.value.filter_config.map(f => ({
        label: f.label,
        key: f.key,
        type: f.type,
        strict_options: f.strict_options,
        options: f.optionsText ? f.optionsText.split(',').map(s => s.trim()).filter(Boolean) : null
      }))
    }

    const formData = new FormData()
    formData.append('data', JSON.stringify(categoryData))
    if (categoryForm.value.file) formData.append('file', categoryForm.value.file)

    await $api('/api/admin/categories', { method: 'POST', body: formData })

    toast.add({ title: 'Успешно', description: 'Категория добавлена', color: 'green' })
    categoryView.value = 'list'
    await fetchCategories()
  } catch (error) {
    const errorMsg = error.data?.detail || error.response?._data?.detail || 'Не удалось создать категорию'
    toast.add({ title: 'Ошибка', description: Array.isArray(errorMsg) ? errorMsg[0].msg : errorMsg, color: 'red' })
  } finally {
    isSubmittingCategory.value = false
  }
}

const confirmDelete = async (category) => {
  if (!confirm(`Удалить категорию «${category.name}»?`)) return
  try {
    await $api(`/api/admin/categories/${category.id}`, { method: 'DELETE' })
    toast.add({ title: 'Успешно', description: 'Категория удалена', color: 'green' })
    await fetchCategories()
  } catch (error) {
    toast.add({ title: 'Ошибка', description: 'Ошибка при удалении', color: 'red' })
  }
}

// --- СПОРЫ ---
const currentUser = useState('user')

const disputes = ref([])
const disputesPending = ref(false)
const disputeView = ref('list') // 'list' | 'detail'

const activeDispute = ref(null)
const activeDisputeMessages = ref([])
const activeOrderMessages = ref([])
const chatPending = ref(false)

const newDisputeMessage = ref('')
const isDisputeSocketConnected = ref(false)
let disputeSocket = null

const formatDate = (value, withTime = false) => {
  if (!value) return '—'

  return new Date(value).toLocaleString('ru-RU', withTime
    ? { dateStyle: 'short', timeStyle: 'short' }
    : { dateStyle: 'medium' },
  )
}

const disputeStatusLabel = (status) => {
  if (status === 'open') return 'Открыт'
  if (status === 'resolved') return 'Решён'
  return status || 'Неизвестно'
}

const disputeStatusClass = (status) => {
  if (status === 'open') return 'bg-amber-100 text-amber-800'
  if (status === 'resolved') return 'bg-green-100 text-green-800'
  return 'bg-gray-100 text-gray-700'
}

const isOwnMessage = (message) => message.sender_id === currentUser.value?.id

const messageAuthorLabel = (message) => (
  isOwnMessage(message)
    ? 'Поддержка'
    : `Участник #${message.sender_id}`
)

const fetchDisputes = async () => {
  disputesPending.value = true

  try {
    disputes.value = await $api('/api/admin/disputes')
  } catch (error) {
    toast.add({
      title: 'Ошибка',
      description: 'Не удалось загрузить список споров',
      color: 'red',
    })
  } finally {
    disputesPending.value = false
  }
}

const disconnectDisputeSocket = () => {
  if (
    disputeSocket &&
    (disputeSocket.readyState === WebSocket.OPEN ||
      disputeSocket.readyState === WebSocket.CONNECTING)
  ) {
    disputeSocket.close()
  }

  disputeSocket = null
  isDisputeSocketConnected.value = false
}

const connectDisputeSocket = () => {
  if (!activeDispute.value || activeDispute.value.status !== 'open') return

  if (
    disputeSocket &&
    disputeSocket.readyState !== WebSocket.CLOSED
  ) {
    return
  }

  const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  const wsUrl = `${wsProtocol}//${window.location.host}/api/ws/disputes/${activeDispute.value.id}/chat`

  disputeSocket = new WebSocket(wsUrl)

  disputeSocket.onopen = () => {
    isDisputeSocketConnected.value = true
  }

  disputeSocket.onmessage = (event) => {
    const message = JSON.parse(event.data)

    if (!activeDisputeMessages.value.some((item) => item.id === message.id)) {
      activeDisputeMessages.value.push(message)
    }
  }

  disputeSocket.onclose = () => {
    isDisputeSocketConnected.value = false
    disputeSocket = null
  }

  disputeSocket.onerror = () => {
    toast.add({
      title: 'Ошибка',
      description: 'Не удалось подключиться к чату спора',
      color: 'red',
    })
  }
}

const reloadDisputeChats = async () => {
  if (!activeDispute.value) return

  chatPending.value = true

  try {
    const [disputeMessages, orderMessages] = await Promise.all([
      $api(`/api/admin/disputes/${activeDispute.value.id}/messages`),
      $api(`/api/admin/orders/${activeDispute.value.order_id}/messages`),
    ])

    activeDisputeMessages.value = disputeMessages
    activeOrderMessages.value = orderMessages
  } catch (error) {
    toast.add({
      title: 'Ошибка',
      description: 'Не удалось загрузить историю сообщений',
      color: 'red',
    })
  } finally {
    chatPending.value = false
  }
}

const openDispute = async (dispute) => {
  disconnectDisputeSocket()

  activeDispute.value = dispute
  activeDisputeMessages.value = []
  activeOrderMessages.value = []
  newDisputeMessage.value = ''
  disputeView.value = 'detail'

  await reloadDisputeChats()
  connectDisputeSocket()
}

const closeDispute = () => {
  disconnectDisputeSocket()
  activeDispute.value = null
  activeDisputeMessages.value = []
  activeOrderMessages.value = []
  newDisputeMessage.value = ''
  disputeView.value = 'list'
}

const sendDisputeMessage = () => {
  const text = newDisputeMessage.value.trim()

  if (
    !text ||
    !disputeSocket ||
    disputeSocket.readyState !== WebSocket.OPEN
  ) {
    return
  }

  disputeSocket.send(text)
  newDisputeMessage.value = ''
}

watch(activeTab, (newTab) => {
  if (newTab === 'categories' && categories.value.length === 0) fetchCategories()
  if (newTab === 'disputes' && disputes.value.length === 0) fetchDisputes()
})

onMounted(() => {
  fetchCategories()
  fetchDisputes()
})

onBeforeUnmount(() => {
  disconnectDisputeSocket()
})

useHead({ title: 'Админ Панель | myMarket' })
</script>

<style scoped>
.animate-fadeIn {
  animation: fadeIn 0.25s ease-out forwards;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(4px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
