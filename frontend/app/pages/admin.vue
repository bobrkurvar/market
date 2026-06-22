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
            <h1 class="text-2xl font-bold text-gray-900">Арбитраж и споры</h1>
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
              Открытых споров нет. Все сделки проходят успешно.
            </div>
            <table v-else class="w-full text-left border-collapse">
              <thead>
                <tr class="bg-gray-50 border-b text-sm text-gray-500">
                  <th class="p-4 font-medium">Спор #</th>
                  <th class="p-4 font-medium">Сумма заказа</th>
                  <th class="p-4 font-medium">Дата открытия</th>
                  <th class="p-4 font-medium text-right">Действие</th>
                </tr>
              </thead>
              <tbody class="divide-y">
                <tr v-for="order in disputes" :key="order.id" class="hover:bg-gray-50 transition">
                  <td class="p-4 font-medium text-gray-900">Заказ #{{ order.id }}</td>
                  <td class="p-4 font-medium text-gray-900">{{ order.price }} ₽</td>
                  <td class="p-4 text-gray-600">{{ new Date(order.created_at).toLocaleDateString() }}</td>
                  <td class="p-4 text-right">
                    <button
                      @click="openDisputeChat(order)"
                      class="inline-flex items-center px-4 py-2 bg-indigo-50 text-indigo-700 text-sm font-medium rounded-lg hover:bg-indigo-100 transition"
                    >
                      Рассмотреть
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div v-else-if="disputeView === 'chat'" class="max-w-4xl mx-auto animate-fadeIn">
          <button
            @click="disputeView = 'list'"
            class="flex items-center text-gray-500 hover:text-gray-900 mb-6 font-medium transition"
          >
            <span class="mr-2">←</span> Назад к списку споров
          </button>

          <div class="bg-white rounded-xl border shadow-sm flex flex-col h-[70vh]">
            <div class="p-6 border-b flex justify-between items-center bg-gray-50 rounded-t-xl">
              <div>
                <h2 class="text-xl font-bold text-gray-900">Спор по заказу #{{ activeDispute?.id }}</h2>
                <p class="text-sm text-gray-500 mt-1">Ознакомьтесь с перепиской и вынесите вердикт</p>
              </div>
            </div>

            <div class="flex-1 overflow-y-auto p-6 space-y-4 bg-gray-50/50">
              <div v-if="chatPending" class="flex justify-center py-10">
                <UIcon name="i-heroicons-arrow-path" class="animate-spin w-8 h-8 text-indigo-500" />
              </div>

              <div v-else-if="activeDisputeMessages.length === 0" class="text-center text-gray-400 mt-10 italic">
                Переписка пуста. Стороны не оставили сообщений.
              </div>

              <div
                v-else
                v-for="msg in activeDisputeMessages"
                :key="msg.id"
                class="flex flex-col"
                :class="msg.sender_id === activeDispute?.buyer_id ? 'items-end' : 'items-start'"
              >
                <span class="text-xs text-gray-500 mb-1 px-1 font-medium">
                  {{ msg.sender_id === activeDispute?.buyer_id ? 'Покупатель' : 'Продавец' }} (ID: {{ msg.sender_id }})
                </span>
                <div
                  class="max-w-[80%] rounded-2xl px-5 py-3 shadow-sm text-sm"
                  :class="msg.sender_id === activeDispute?.buyer_id
                    ? 'bg-indigo-100 text-indigo-900 rounded-br-none'
                    : 'bg-white border border-gray-200 text-gray-800 rounded-bl-none'"
                >
                  <p class="whitespace-pre-wrap leading-relaxed">{{ msg.text }}</p>
                </div>
              </div>
            </div>

            <div class="p-6 border-t bg-white rounded-b-xl flex gap-4">
              <button
                @click="resolveDispute('buyer')"
                :disabled="isResolving"
                class="flex-1 bg-red-50 text-red-700 border border-red-200 px-6 py-3 rounded-lg font-medium hover:bg-red-100 transition flex items-center justify-center disabled:opacity-50"
              >
                Вернуть деньги покупателю
              </button>
              <button
                @click="resolveDispute('seller')"
                :disabled="isResolving"
                class="flex-1 bg-green-50 text-green-700 border border-green-200 px-6 py-3 rounded-lg font-medium hover:bg-green-100 transition flex items-center justify-center disabled:opacity-50"
              >
                Отклонить спор (Деньги продавцу)
              </button>
            </div>
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
import { ref, onMounted, watch } from 'vue'

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
const disputeView = ref('list')  // 'list' | 'chat'

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
const disputes = ref([])
const disputesPending = ref(false)
const activeDispute = ref(null)
const activeDisputeMessages = ref([])
const chatPending = ref(false)
const isResolving = ref(false)

const fetchDisputes = async () => {
  disputesPending.value = true
  try {
    disputes.value = await $api('/api/admin/orders/disputes')
  } catch (error) {
    toast.add({ title: 'Ошибка', description: 'Не удалось загрузить споры', color: 'red' })
  } finally {
    disputesPending.value = false
  }
}

const openDisputeChat = async (order) => {
  activeDispute.value = order
  disputeView.value = 'chat'
  chatPending.value = true
  activeDisputeMessages.value = []

  try {
    activeDisputeMessages.value = await $api(`/api/admin/orders/${order.id}/messages`)
  } catch (error) {
    toast.add({ title: 'Ошибка', description: 'Не удалось загрузить переписку', color: 'red' })
  } finally {
    chatPending.value = false
  }
}

const resolveDispute = async (winner) => {
  const winnerName = winner === 'buyer' ? 'покупателя (возврат)' : 'продавца (закрыть спор)'
  if (!confirm(`Вы уверены, что хотите решить спор в пользу ${winnerName}?`)) return

  isResolving.value = true
  try {
    await $api(`/api/admin/orders/${activeDispute.value.id}/resolve`, {
      method: 'POST',
      body: { winner }
    })

    toast.add({ title: 'Успешно', description: 'Решение принято', color: 'green' })
    disputeView.value = 'list'
    await fetchDisputes()
  } catch (error) {
    const errorMsg = error.data?.detail || error.response?._data?.detail || 'Ошибка при решении спора'
    toast.add({ title: 'Ошибка', description: errorMsg, color: 'red' })
  } finally {
    isResolving.value = false
  }
}

watch(activeTab, (newTab) => {
  if (newTab === 'categories' && categories.value.length === 0) fetchCategories()
  if (newTab === 'disputes' && disputes.value.length === 0) fetchDisputes()
})

onMounted(() => {
  fetchCategories()
  fetchDisputes()
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
