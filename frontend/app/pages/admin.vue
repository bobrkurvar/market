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
          <UButton
            icon="i-heroicons-arrow-left-on-rectangle"
            color="gray"
            variant="ghost"
            size="sm"
            to="/"
            title="Вернуться на сайт"
          />
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
          <UButton icon="i-heroicons-plus" color="primary" @click="openCreateModal(null)">
            Создать корень
          </UButton>
        </div>

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
                <UIcon
                  :name="cat.has_children ? 'i-heroicons-folder-open' : 'i-heroicons-document-text'"
                  :class="cat.has_children ? 'text-amber-500 w-5 h-5' : 'text-gray-400 w-4 h-4'"
                />
                <span :class="{ 'font-bold text-gray-900 dark:text-white': cat.level === 0, 'text-gray-700 dark:text-gray-300': cat.level > 0 }">
                  {{ cat.name }}
                </span>
              </div>
              <div class="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                <UButton icon="i-heroicons-plus-circle" color="gray" variant="ghost" size="xs" title="Добавить подкатегорию" @click="openCreateModal(cat)" />
                <UButton icon="i-heroicons-trash" color="red" variant="ghost" size="xs" title="Удалить" @click="confirmDelete(cat)" />
              </div>
            </div>
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

    <UModal v-model="isModalOpen">
      <UCard :ui="{ ring: '', divide: 'divide-y divide-gray-100 dark:divide-gray-800' }">
        <template #header>
          <div class="flex items-center justify-between">
            <h3 class="text-base font-semibold leading-6 text-gray-900 dark:text-white">
              {{ categoryForm.parent_id ? `Новая подкатегория для «${categoryForm.parent_name}»` : 'Новый корневой раздел' }}
            </h3>
            <UButton color="gray" variant="ghost" icon="i-heroicons-x-mark" class="-my-1" @click="isModalOpen = false" />
          </div>
        </template>

        <form @submit.prevent="submitCategory" class="space-y-4 py-2">
          <UFormGroup label="Название категории" required>
            <UInput v-model="categoryForm.name" placeholder="Например: Ключи Steam, VPN, Подписки..." autofocus required />
          </UFormGroup>

          <div class="flex justify-end gap-3 pt-4">
            <UButton color="gray" variant="ghost" @click="isModalOpen = false">Отмена</UButton>
            <UButton type="submit" color="primary" :loading="isSubmittingCategory">Создать</UButton>
          </div>
        </form>
      </UCard>
    </UModal>

  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'

// ВАЖНО: Отключаем дефолтный макет сайта (затираем общую синюю шапку)
definePageMeta({
  layout: false
})

const toast = useToast()
const { $api } = useNuxtApp()

const currentTab = ref('categories')
const tabs = [
  { id: 'dashboard', name: 'Главная / Обзор', icon: 'i-heroicons-squares-2x2' },
  { id: 'categories', name: 'Категории каталога', icon: 'i-heroicons-rectangle-stack' },
  { id: 'products', name: 'Модерация товаров', icon: 'i-heroicons-shield-check' }
]

const mockStats = [
  { title: 'Оборот платформы', value: '1 245 000 ₽', icon: 'i-heroicons-banknotes', iconColor: 'text-green-500', bgColor: 'bg-green-50 dark:bg-green-950/40' },
  { title: 'Всего продавцов', value: '342 акк.', icon: 'i-heroicons-users', iconColor: 'text-blue-500', bgColor: 'bg-blue-50 dark:bg-blue-950/40' }
]

const categories = ref([])
const categoriesPending = ref(false)
const isModalOpen = ref(false)
const isSubmittingCategory = ref(false)

const categoryForm = ref({
  name: '',
  parent_id: null,
  parent_name: ''
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

const openCreateModal = (parentCategory = null) => {
  categoryForm.value.name = ''
  if (parentCategory) {
    categoryForm.value.parent_id = parentCategory.id
    categoryForm.value.parent_name = parentCategory.name
  } else {
    categoryForm.value.parent_id = null
    categoryForm.value.parent_name = ''
  }
  isModalOpen.value = true
}

const submitCategory = async () => {
  if (!categoryForm.value.name.trim()) return
  isSubmittingCategory.value = true
  try {
    await $api('/api/admin/category', {
      method: 'POST',
      body: {
        name: categoryForm.value.name,
        parent_id: categoryForm.value.parent_id
      }
    })
    toast.add({ title: 'Успешно', description: 'Категория добавлена в структуру', color: 'green' })
    isModalOpen.value = false
    await fetchCategories()
  } catch (error) {
    toast.add({ title: 'Ошибка', description: 'Не удалось создать категорию', color: 'red' })
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

watch(currentTab, (newTab) => {
  if (newTab === 'categories' && categories.value.length === 0) {
    fetchCategories()
  }
})

onMounted(() => {
  if (currentTab.value === 'categories') {
    fetchCategories()
  }
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
