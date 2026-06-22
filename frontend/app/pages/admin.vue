<template>
  <div class="min-h-screen bg-gray-100 dark:bg-gray-950 font-sans text-gray-900 dark:text-gray-100">

    <header class="bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800 sticky top-0 z-40 shadow-sm">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <UIcon name="i-heroicons-wrench-screwdriver" class="w-6 h-6 text-primary-500" />
          <h2 class="text-xl font-black tracking-tight flex items-center gap-2">
            myMarket
            <span class="text-xs font-normal text-primary-500 bg-primary-50 dark:bg-primary-950/50 px-2 py-0.5 rounded">
              Панель администратора
            </span>
          </h2>
        </div>

        <nav class="flex items-center gap-1">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            @click="currentTab = tab.id"
            :class="[
              currentTab === tab.id
                ? 'bg-primary-50 dark:bg-primary-950 text-primary-600 dark:text-primary-400 font-semibold shadow-sm'
                : 'text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-800/50 hover:text-gray-900 dark:hover:text-white'
            ]"
            class="flex items-center gap-2 px-4 py-2 rounded-lg text-sm transition-colors"
          >
            <UIcon :name="tab.icon" class="w-4 h-4" />
            <span>{{ tab.name }}</span>
          </button>
        </nav>

        <div class="flex items-center gap-4 border-l border-gray-200 dark:border-gray-800 pl-4">
          <div class="text-right hidden sm:block">
            <p class="text-xs font-bold">Администратор</p>
            <p class="text-[10px] text-gray-400">admin@mymarket.ru</p>
          </div>
          <UButton icon="i-heroicons-arrow-left-on-rectangle" color="gray" variant="ghost" size="sm" to="/" title="Вернуться на сайт" />
        </div>
      </div>
    </header>

    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">

      <div v-if="currentTab === 'dashboard'" class="space-y-8 animate-fadeIn">
        <div>
          <h1 class="text-3xl font-extrabold">Главная панель</h1>
          <p class="text-sm text-gray-500 mt-1">Основные показатели платформы</p>
        </div>
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          <UCard v-for="stat in mockStats" :key="stat.title" class="shadow-sm">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-sm text-gray-500 font-medium">{{ stat.title }}</p>
                <p class="text-2xl font-bold mt-2">{{ stat.value }}</p>
              </div>
              <div :class="stat.bgColor" class="p-3 rounded-xl">
                <UIcon :name="stat.icon" :class="stat.iconColor" class="w-6 h-6" />
              </div>
            </div>
          </UCard>
        </div>
      </div>

      <div v-if="currentTab === 'categories'" class="space-y-6 animate-fadeIn">
        <div class="flex justify-between items-center border-b border-gray-200 dark:border-gray-800 pb-4">
          <div>
            <h1 class="text-3xl font-extrabold">Дерево категорий</h1>
            <p class="text-sm text-gray-500 mt-1">Управление уровнями вложенности и иерархией каталога</p>
          </div>
          <UButton
            :icon="showCreateForm ? 'i-heroicons-x-mark' : 'i-heroicons-plus'"
            :color="showCreateForm ? 'gray' : 'primary'"
            @click="toggleCreateForm(null)"
          >
            {{ showCreateForm ? 'Закрыть форму' : 'Создать корень' }}
          </UButton>
        </div>

        <UCard v-if="showCreateForm" class="mb-6 border border-primary-200 dark:border-primary-800 shadow-sm animate-fadeIn bg-primary-50/30 dark:bg-primary-950/20">
          <template #header>
            <h3 class="text-base font-semibold leading-6 text-gray-900 dark:text-white">
              {{ categoryForm.parent_id ? `Новая подкатегория для «${categoryForm.parent_name}»` : 'Новый корневой раздел' }}
            </h3>
          </template>

          <form @submit.prevent="submitCategory" class="space-y-8">
            <div class="space-y-4">
              <h4 class="font-medium text-gray-700 dark:text-gray-300 border-b border-gray-200 dark:border-gray-800 pb-2">Основные настройки</h4>

              <UFormGroup label="Название категории" required>
                <UInput
                  v-model="categoryForm.name"
                  placeholder="Например: Ключи Steam..."
                  autofocus
                  required
                />
              </UFormGroup>

              <div>
                <span class="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">
                  Логотип (иконка)
                </span>
                <div class="flex items-center gap-4 mt-1">
                  <UButton color="white" icon="i-heroicons-arrow-up-tray" @click="$refs.fileInputRef.click()">
                    Выбрать файл
                  </UButton>
                  <span class="text-sm text-gray-500 truncate max-w-[200px]">
                    {{ categoryForm.file ? categoryForm.file.name : 'Файл не выбран' }}
                  </span>
                </div>
                <input
                  type="file"
                  accept="image/png, image/jpeg, image/webp, image/svg+xml"
                  class="hidden"
                  @change="handleFileChange"
                  ref="fileInputRef"
                />
                <p class="text-xs text-gray-500 mt-2">Форматы: PNG, WebP, SVG. Фон должен быть прозрачным.</p>
              </div>
            </div>

            <div class="space-y-4">
              <div class="flex items-center justify-between border-b border-gray-200 dark:border-gray-800 pb-2">
                <h4 class="font-medium text-gray-700 dark:text-gray-300">Атрибуты и фильтры</h4>
                <UButton size="xs" color="indigo" variant="soft" icon="i-heroicons-plus" @click="addFilter">
                  Добавить свойство
                </UButton>
              </div>

              <div v-if="categoryForm.filter_config.length === 0" class="text-sm text-gray-400 italic text-center py-4 bg-white dark:bg-gray-900 rounded-lg border border-dashed border-gray-300 dark:border-gray-700">
                Специфичных фильтров нет. Продавцы смогут указывать только базовую цену.
              </div>

              <div class="space-y-4">
                <div v-for="(filter, index) in categoryForm.filter_config" :key="index" class="bg-white dark:bg-gray-900 p-4 rounded-lg border border-gray-200 dark:border-gray-800 shadow-sm relative group">
                  <UButton
                    icon="i-heroicons-x-mark"
                    color="red"
                    variant="ghost"
                    size="xs"
                    class="absolute top-2 right-2 opacity-50 group-hover:opacity-100 transition-opacity"
                    @click="removeFilter(index)"
                  />

                  <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-4">
                    <UFormGroup label="Название (Label)" required>
                      <UInput v-model="filter.label" placeholder="Напр: Платформа" required />
                    </UFormGroup>
                    <UFormGroup label="Системный ключ (Key)" required>
                      <UInput v-model="filter.key" placeholder="Напр: platform" required />
                    </UFormGroup>
                  </div>

                  <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 items-end">
                    <UFormGroup label="Тип интерфейса (UI)" required>
                      <USelect v-model="filter.type" :options="uiTypeOptions" required />
                    </UFormGroup>
                    <div class="pb-2">
                      <UCheckbox v-model="filter.strict_options" label="Строгая валидация" />
                    </div>
                  </div>

                  <div class="mt-4" v-if="['select', 'checkbox', 'radio'].includes(filter.type)">
                    <UFormGroup label="Доступные варианты (через запятую)">
                      <UInput v-model="filter.optionsText" placeholder="Напр: Steam, Epic Games" />
                    </UFormGroup>
                  </div>
                </div>
              </div>
            </div>

            <div class="flex justify-end gap-3 pt-4 border-t border-gray-200 dark:border-gray-800">
              <UButton color="gray" variant="ghost" @click="showCreateForm = false">Отмена</UButton>
              <UButton type="submit" color="primary" :loading="isSubmittingCategory">Создать категорию</UButton>
            </div>
          </form>
        </UCard>

        <div v-if="categoriesPending" class="flex justify-center py-20">
          <UIcon name="i-heroicons-arrow-path" class="animate-spin w-10 h-10 text-primary-500" />
        </div>

        <div v-else class="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 shadow-sm overflow-hidden">
          <div v-if="categories.length === 0" class="p-12 text-center text-gray-400">
            Каталог пуст. Создайте первую категорию, чтобы начать.
          </div>
          <div v-else class="divide-y divide-gray-100 dark:divide-gray-800">
            <div
              v-for="cat in categories"
              :key="cat.id"
              class="flex items-center justify-between p-4 hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors group"
              :style="{ paddingLeft: `${cat.level * 24 + 16}px` }"
            >
              <div class="flex items-center gap-3">
                <div class="w-8 h-8 flex-shrink-0 flex items-center justify-center bg-gray-50 dark:bg-gray-800 rounded border border-gray-100 dark:border-gray-700 overflow-hidden">
                   <img v-if="cat.search_url" :src="cat.search_url" :alt="cat.name" class="w-full h-full object-contain p-1" />
                   <UIcon v-else :name="cat.has_children ? 'i-heroicons-folder-open' : 'i-heroicons-document-text'" :class="cat.has_children ? 'text-amber-500 w-5 h-5' : 'text-gray-400 w-4 h-4'" />
                </div>
                <span :class="{ 'font-bold text-gray-900 dark:text-white': cat.level === 0, 'text-gray-700 dark:text-gray-300': cat.level > 0 }">
                  {{ cat.name }}
                </span>
              </div>
              <div class="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                <UButton icon="i-heroicons-plus-circle" color="gray" variant="ghost" size="xs" title="Добавить" @click="toggleCreateForm(cat)" />
                <UButton icon="i-heroicons-trash" color="red" variant="ghost" size="xs" title="Удалить" @click="confirmDelete(cat)" />
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-if="currentTab === 'disputes'" class="space-y-6 animate-fadeIn">
        <div class="flex justify-between items-center border-b border-gray-200 dark:border-gray-800 pb-4">
          <div>
            <h1 class="text-3xl font-extrabold">Арбитраж / Споры</h1>
            <p class="text-sm text-gray-500 mt-1">Рассмотрение жалоб и возврат средств</p>
          </div>
          <UButton icon="i-heroicons-arrow-path" color="gray" variant="ghost" @click="fetchDisputes">Обновить</UButton>
        </div>

        <div v-if="disputesPending" class="flex justify-center py-20">
          <UIcon name="i-heroicons-arrow-path" class="animate-spin w-10 h-10 text-primary-500" />
        </div>

        <div v-else class="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 shadow-sm overflow-hidden">
          <div v-if="disputes.length === 0" class="p-12 text-center text-gray-400">
            <UIcon name="i-heroicons-check-badge" class="w-16 h-16 mx-auto mb-3 text-green-500/50" />
            <p class="font-medium">Открытых споров нет. Все счастливы!</p>
          </div>

          <div v-else class="overflow-x-auto">
            <table class="w-full text-sm text-left text-gray-500 dark:text-gray-400">
              <thead class="text-xs text-gray-700 uppercase bg-gray-50 dark:bg-gray-800/50 dark:text-gray-300">
                <tr>
                  <th scope="col" class="px-6 py-3">ID Заказа</th>
                  <th scope="col" class="px-6 py-3">Сумма</th>
                  <th scope="col" class="px-6 py-3">Дата открытия</th>
                  <th scope="col" class="px-6 py-3 text-right">Действие</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-100 dark:divide-gray-800">
                <tr v-for="order in disputes" :key="order.id" class="hover:bg-gray-50 dark:hover:bg-gray-800/20 transition-colors">
                  <td class="px-6 py-4 font-bold text-gray-900 dark:text-white">
                    #{{ order.id }}
                  </td>
                  <td class="px-6 py-4 font-medium text-gray-900 dark:text-white">
                    {{ order.price }} ₽
                  </td>
                  <td class="px-6 py-4">
                    {{ new Date(order.created_at).toLocaleDateString() }}
                  </td>
                  <td class="px-6 py-4 text-right">
                    <UButton size="sm" color="primary" variant="soft" icon="i-heroicons-eye" @click="openDisputeModal(order)">
                      Рассмотреть
                    </UButton>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <div v-if="currentTab === 'products'" class="space-y-6 animate-fadeIn">
        <div>
          <h1 class="text-3xl font-extrabold">Модерация товаров</h1>
          <p class="text-sm text-gray-500 mt-1">Проверка объявлений от продавцов</p>
        </div>
        <div class="bg-white dark:bg-gray-900 rounded-xl border border-dashed border-gray-300 dark:border-gray-700 p-12 text-center text-gray-400">
          <p class="font-medium">Все товары проверены</p>
        </div>
      </div>

    </main>

    <USlideover v-model="isDisputeModalOpen" class="w-full md:w-[600px] max-w-full">
      <div class="flex flex-col h-full bg-white dark:bg-gray-900">

        <div class="p-4 border-b border-gray-200 dark:border-gray-800 flex justify-between items-center bg-gray-50 dark:bg-gray-950">
          <div>
            <h2 class="text-lg font-bold">Спор по заказу #{{ activeDispute?.id }}</h2>
            <p class="text-sm text-gray-500">Оцените переписку и примите решение</p>
          </div>
          <UButton color="gray" variant="ghost" icon="i-heroicons-x-mark" @click="isDisputeModalOpen = false" />
        </div>

        <div class="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50/50 dark:bg-gray-900/50">
          <div v-if="chatPending" class="flex justify-center py-10">
            <UIcon name="i-heroicons-arrow-path" class="animate-spin w-8 h-8 text-gray-400" />
          </div>

          <div v-else-if="activeDisputeMessages.length === 0" class="text-center text-gray-400 mt-10">
            Переписка пуста
          </div>

          <div
            v-else
            v-for="msg in activeDisputeMessages"
            :key="msg.id"
            class="flex flex-col mb-4"
            :class="msg.sender_id === activeDispute?.buyer_id ? 'items-end' : 'items-start'"
          >
            <span class="text-[10px] text-gray-500 mb-1 px-1">
              {{ msg.sender_id === activeDispute?.buyer_id ? 'Покупатель' : 'Продавец' }} ID: {{ msg.sender_id }}
            </span>
            <div
              class="max-w-[85%] rounded-2xl px-4 py-2 shadow-sm text-sm"
              :class="msg.sender_id === activeDispute?.buyer_id
                ? 'bg-blue-100 dark:bg-blue-900/40 text-blue-900 dark:text-blue-100 rounded-br-none'
                : 'bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-bl-none'"
            >
              <p class="whitespace-pre-wrap">{{ msg.text }}</p>
            </div>
          </div>
        </div>

        <div class="p-4 border-t border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-950 space-y-3">
          <UButton
            color="red"
            block
            size="lg"
            icon="i-heroicons-arrow-uturn-left"
            :loading="isResolving"
            @click="resolveDispute('buyer')"
          >
            Решить в пользу покупателя (Возврат средств)
          </UButton>
          <UButton
            color="green"
            block
            size="lg"
            variant="soft"
            icon="i-heroicons-check"
            :loading="isResolving"
            @click="resolveDispute('seller')"
          >
            Решить в пользу продавца (Отклонить спор)
          </UButton>
        </div>

      </div>
    </USlideover>

  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'

definePageMeta({
  layout: false
})

const toast = useToast()
const { $api } = useNuxtApp()

const currentTab = ref('categories')
const tabs = [
  { id: 'dashboard', name: 'Главная / Обзор', icon: 'i-heroicons-squares-2x2' },
  { id: 'categories', name: 'Категории каталога', icon: 'i-heroicons-rectangle-stack' },
  { id: 'disputes', name: 'Арбитраж / Споры', icon: 'i-heroicons-scale' },
  { id: 'products', name: 'Модерация товаров', icon: 'i-heroicons-shield-check' }
]

const uiTypeOptions = [
  { label: 'Выпадающий список (Select)', value: 'select' },
  { label: 'Множественный выбор (Checkbox)', value: 'checkbox' },
  { label: 'Одиночный выбор (Radio)', value: 'radio' },
  { label: 'Диапазон ОТ и ДО (Range)', value: 'range' }
]

const mockStats = [
  { title: 'Оборот платформы', value: '1 245 000 ₽', icon: 'i-heroicons-banknotes', iconColor: 'text-green-500', bgColor: 'bg-green-50 dark:bg-green-950/40' },
  { title: 'Всего продавцов', value: '342 акк.', icon: 'i-heroicons-users', iconColor: 'text-blue-500', bgColor: 'bg-blue-50 dark:bg-blue-950/40' }
]

// --- КАТЕГОРИИ ---
const categories = ref([])
const categoriesPending = ref(false)
const showCreateForm = ref(false)
const isSubmittingCategory = ref(false)
const fileInputRef = ref(null)

const categoryForm = ref({
  name: '',
  parent_id: null,
  parent_name: '',
  file: null,
  filter_config: []
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

const toggleCreateForm = (parentCategory = null) => {
  if (showCreateForm.value && !parentCategory && !categoryForm.value.parent_id) {
    showCreateForm.value = false
    return
  }

  categoryForm.value.name = ''
  categoryForm.value.file = null
  categoryForm.value.filter_config = []
  if (fileInputRef.value) fileInputRef.value.value = ''

  if (parentCategory) {
    categoryForm.value.parent_id = parentCategory.id
    categoryForm.value.parent_name = parentCategory.name
  } else {
    categoryForm.value.parent_id = null
    categoryForm.value.parent_name = ''
  }

  showCreateForm.value = true
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const handleFileChange = (event) => {
  const files = event.target.files
  if (files && files.length > 0) {
    categoryForm.value.file = files[0]
  } else {
    categoryForm.value.file = null
  }
}

const addFilter = () => {
  categoryForm.value.filter_config.push({
    label: '',
    key: '',
    type: 'select',
    strict_options: true,
    optionsText: ''
  })
}

const removeFilter = (index) => {
  categoryForm.value.filter_config.splice(index, 1)
}

const submitCategory = async () => {
  if (!categoryForm.value.name.trim()) return
  isSubmittingCategory.value = true

  try {
    const categoryData = {
      name: categoryForm.value.name,
      parent_id: categoryForm.value.parent_id || null,
      filter_config: categoryForm.value.filter_config.map(f => {
        const optionsArray = f.optionsText
          ? f.optionsText.split(',').map(s => s.trim()).filter(Boolean)
          : null

        return {
          label: f.label,
          key: f.key,
          type: f.type,
          strict_options: f.strict_options,
          options: optionsArray
        }
      })
    }

    const formData = new FormData()
    formData.append('data', JSON.stringify(categoryData))

    if (categoryForm.value.file) {
      formData.append('file', categoryForm.value.file)
    }

    await $api('/api/admin/categories', {
      method: 'POST',
      body: formData
    })

    toast.add({ title: 'Успешно', description: 'Категория добавлена', color: 'green' })
    showCreateForm.value = false
    await fetchCategories()
  } catch (error) {
    const errorMsg = error.data?.detail || error.response?._data?.detail || 'Не удалось создать категорию'
    toast.add({ title: 'Ошибка', description: Array.isArray(errorMsg) ? errorMsg[0].msg : errorMsg, color: 'red' })
  } finally {
    isSubmittingCategory.value = false
  }
}

const confirmDelete = async (category) => {
  if (!confirm(`Удалить категорию «${category.name}» и все её подкатегории?`)) return
  try {
    await $api(`/api/admin/categories/${category.id}`, { method: 'DELETE' })
    toast.add({ title: 'Успешно', description: 'Категория удалена', color: 'green' })
    await fetchCategories()
  } catch (error) {
    toast.add({ title: 'Ошибка', description: 'Ошибка при удалении', color: 'red' })
  }
}

// --- СПОРЫ (АРБИТРАЖ) ---
const disputes = ref([])
const disputesPending = ref(false)
const isDisputeModalOpen = ref(false)
const activeDispute = ref(null)
const activeDisputeMessages = ref([])
const chatPending = ref(false)
const isResolving = ref(false)

const fetchDisputes = async () => {
  disputesPending.value = true
  try {
    // Используем твой новый эндпоинт
    disputes.value = await $api('/api/admin/orders/disputes')
  } catch (error) {
    toast.add({ title: 'Ошибка', description: 'Не удалось загрузить список споров', color: 'red' })
  } finally {
    disputesPending.value = false
  }
}

const openDisputeModal = async (order) => {
  activeDispute.value = order
  isDisputeModalOpen.value = true
  chatPending.value = true
  activeDisputeMessages.value = []

  try {
    // Получаем переписку
    activeDisputeMessages.value = await $api(`/api/admin/orders/${order.id}/messages`)
  } catch (error) {
    toast.add({ title: 'Ошибка', description: 'Не удалось загрузить переписку', color: 'red' })
  } finally {
    chatPending.value = false
  }
}

const resolveDispute = async (winner) => {
  const winnerName = winner === 'buyer' ? 'покупателя (сделать возврат)' : 'продавца (закрыть спор)'
  if (!confirm(`Вы уверены, что хотите решить спор в пользу ${winnerName}?`)) return

  isResolving.value = true
  try {
    // ЭТОТ ЭНДПОИНТ НАМ ПРЕДСТОИТ НАПИСАТЬ НА БЭКЕНДЕ
    await $api(`/api/admin/orders/${activeDispute.value.id}/resolve`, {
      method: 'POST',
      body: { winner } // 'buyer' или 'seller'
    })

    toast.add({ title: 'Успешно', description: 'Решение по спору принято', color: 'green' })
    isDisputeModalOpen.value = false
    await fetchDisputes()
  } catch (error) {
    const errorMsg = error.data?.detail || error.response?._data?.detail || 'Ошибка при решении спора'
    toast.add({ title: 'Ошибка', description: errorMsg, color: 'red' })
  } finally {
    isResolving.value = false
  }
}

// --- НАБЛЮДАТЕЛИ ---
watch(currentTab, (newTab) => {
  if (newTab === 'categories' && categories.value.length === 0) {
    fetchCategories()
  }
  if (newTab === 'disputes' && disputes.value.length === 0) {
    fetchDisputes()
  }
})

onMounted(() => {
  if (currentTab.value === 'categories') fetchCategories()
  if (currentTab.value === 'disputes') fetchDisputes()
})

useHead({ title: 'Панель управления | Администратор' })
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
