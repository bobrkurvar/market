<template>
  <div class="min-h-screen bg-gray-50 font-sans text-gray-900">
    <main class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">

      <div v-if="currentView === 'list'" class="space-y-6 animate-fadeIn">
        <div class="flex justify-between items-center">
          <h1 class="text-2xl font-bold text-gray-900">Мои товары</h1>
          <button
            @click="currentView = 'create'"
            class="bg-indigo-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-indigo-700 transition shadow-sm"
          >
            + Добавить товар
          </button>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div class="bg-white p-6 rounded-xl border shadow-sm">
            <div class="text-sm text-gray-500 mb-1">Активных товаров</div>
            <div class="text-3xl font-bold">{{ products.length }}</div>
          </div>
          <div class="bg-white p-6 rounded-xl border shadow-sm">
            <div class="text-sm text-gray-500 mb-1">Продано за месяц</div>
            <div class="text-3xl font-bold text-green-600">142 шт.</div>
          </div>
          <div class="bg-white p-6 rounded-xl border shadow-sm">
            <div class="text-sm text-gray-500 mb-1">Баланс</div>
            <div class="text-3xl font-bold">45 200 ₽</div>
          </div>
        </div>

        <div class="bg-white rounded-xl border shadow-sm overflow-hidden">
          <div v-if="products.length === 0" class="p-12 text-center text-gray-500">
            У вас пока нет ни одного товара. Нажмите "+ Добавить товар", чтобы начать продажи.
          </div>
          <table v-else class="w-full text-left border-collapse">
            <thead>
              <tr class="bg-gray-50 border-b text-sm text-gray-500">
                <th class="p-4 font-medium">Название</th>
                <th class="p-4 font-medium">Вариантов</th>
                <th class="p-4 font-medium">Ключей в наличии</th>
                <th class="p-4 font-medium text-right">Действия</th>
              </tr>
            </thead>
            <tbody class="divide-y">
              <tr v-for="product in products" :key="product.id" class="hover:bg-gray-50 transition">
                <td class="p-4 font-medium text-gray-900">{{ product.title }}</td>
                <td class="p-4 text-gray-600">{{ product.variants_count }} опций</td>
                <td class="p-4">
                  <span class="bg-green-100 text-green-800 text-xs px-2 py-1 rounded-full font-medium">
                    {{ product.items_count }} шт.
                  </span>
                </td>
                <td class="p-4 text-right space-x-3">
                  <button class="text-indigo-600 hover:underline text-sm">Изменить</button>
                  <button class="text-red-600 hover:underline text-sm">Удалить</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div v-else-if="currentView === 'create'" class="max-w-4xl mx-auto animate-fadeIn">
        <button
          @click="currentView = 'list'"
          class="flex items-center text-gray-500 hover:text-gray-900 mb-6 font-medium transition"
        >
          <span class="mr-2">←</span> Назад к списку
        </button>

        <div class="bg-white p-8 rounded-xl border shadow-sm">
          <h2 class="text-2xl font-bold mb-8">Создание нового товара</h2>

          <form @submit.prevent="submitProduct" class="space-y-8">
            <section>
              <h3 class="text-lg font-semibold mb-4 border-b pb-2">Основная информация</h3>
              <div class="space-y-4">
                <div>
                  <label class="block text-sm font-medium mb-1">Название товара <span class="text-red-500">*</span></label>
                  <input v-model="form.title" type="text" required placeholder="Например: Подписка Spotify Premium" class="w-full border border-gray-300 rounded-lg p-3 focus:ring-2 focus:ring-indigo-500 focus:outline-none" />
                </div>

                <div>
                  <label class="block text-sm font-medium mb-1">Категория товара <span class="text-red-500">*</span></label>
                  <select
                    v-model="form.category_id"
                    @change="onCategoryChange"
                    required
                    class="w-full border border-gray-300 rounded-lg p-3 bg-white focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                  >
                    <option value="" disabled>Выберите категорию...</option>
                    <option v-for="cat in categories" :key="cat.id" :value="cat.id">
                      {{ cat.name }}
                    </option>
                  </select>
                </div>

                <div>
                  <label class="block text-sm font-medium mb-1">Описание</label>
                  <textarea v-model="form.description" rows="3" placeholder="Подробное описание товара..." class="w-full border border-gray-300 rounded-lg p-3 focus:ring-2 focus:ring-indigo-500 focus:outline-none"></textarea>
                </div>

                <div>
                  <label class="block text-sm font-medium mb-1">Изображение товара <span class="text-red-500">*</span></label>
                  <input
                    type="file"
                    accept="image/*"
                    @change="onFileChange"
                    class="w-full border border-gray-300 rounded-lg p-3 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100"
                  />
                  <p v-if="imageFile" class="text-sm text-gray-500 mt-1">Выбран: {{ imageFile.name }}</p>
                </div>
              </div>
            </section>

            <section>
              <div class="flex justify-between items-center mb-4 border-b pb-2">
                <h3 class="text-lg font-semibold">Опции и ключи</h3>
                <button type="button" @click="addVariant" class="text-indigo-600 hover:underline text-sm font-medium flex items-center">
                  <span>+ Добавить вариант товара</span>
                </button>
              </div>

              <div class="space-y-6">
                <div v-for="(variant, index) in form.variants" :key="index" class="bg-gray-50 p-6 rounded-lg border border-gray-200 relative group">
                  <button v-if="form.variants.length > 1" type="button" @click="removeVariant(index)" class="absolute top-4 right-4 text-gray-400 hover:text-red-500 transition opacity-0 group-hover:opacity-100" title="Удалить опцию">
                    ✕
                  </button>

                  <h4 class="font-medium text-gray-700 mb-4">Вариант #{{ index + 1 }}</h4>

                  <div class="mb-5">
                    <label class="block text-sm font-medium mb-1">Цена (₽) <span class="text-red-500">*</span></label>
                    <input v-model.number="variant.price" type="number" min="0" required class="w-full md:w-1/2 border border-gray-300 rounded-lg p-3 focus:ring-2 focus:ring-indigo-500 focus:outline-none" />
                  </div>

                  <div class="mb-5 grid grid-cols-1 md:grid-cols-2 gap-6">

                    <div v-if="strictFilters.length > 0" class="bg-white p-4 rounded-lg border shadow-sm">
                      <h5 class="text-sm font-semibold text-gray-700 mb-3 border-b pb-1">Системные характеристики</h5>
                      <div class="space-y-4">
                        <div v-for="filter in strictFilters" :key="filter.key">
                          <label class="block text-xs font-medium text-gray-600 mb-1">
                            {{ filter.label }} <span class="text-red-500">*</span>
                          </label>

                          <div v-if="filter.type === 'checkbox'" class="flex flex-wrap gap-2">
                            <label v-for="opt in filter.options" :key="opt" class="flex items-center space-x-1 bg-gray-50 border px-2 py-1 rounded text-sm cursor-pointer hover:bg-gray-100">
                              <input type="checkbox" :value="opt" v-model="variant.systemAttributes[filter.key]" class="text-indigo-600 focus:ring-indigo-500 rounded-sm">
                              <span>{{ opt }}</span>
                            </label>
                          </div>

                          <select v-else v-model="variant.systemAttributes[filter.key]" required class="w-full border border-gray-300 rounded p-2 text-sm focus:ring-2 focus:ring-indigo-500 focus:outline-none">
                            <option value="" disabled>Выберите...</option>
                            <option v-for="opt in filter.options" :key="opt" :value="opt">{{ opt }}</option>
                          </select>
                        </div>
                      </div>
                    </div>

                    <div class="bg-white p-4 rounded-lg border shadow-sm flex flex-col">
                      <div class="flex justify-between items-center mb-3 border-b pb-1">
                        <h5 class="text-sm font-semibold text-gray-700">Свои характеристики</h5>
                        <button type="button" @click="addCustomAttribute(variant)" class="text-xs text-indigo-600 hover:text-indigo-800 font-medium bg-indigo-50 px-2 py-1 rounded transition">
                          + Добавить
                        </button>
                      </div>

                      <div class="space-y-2 flex-grow">
                        <div v-if="variant.customAttributes.length === 0" class="text-xs text-gray-400 italic mt-4 text-center">
                          Нет дополнительных характеристик
                        </div>
                        <div v-for="(attr, attrIdx) in variant.customAttributes" :key="attrIdx" class="flex gap-2 items-center">
                          <input v-model="attr.key" type="text" placeholder="Название (напр. Язык)" class="w-1/2 border border-gray-300 rounded p-2 text-sm focus:ring-2 focus:ring-indigo-500 focus:outline-none" />
                          <input v-model="attr.value" type="text" placeholder="Значение (напр. Русский)" class="w-1/2 border border-gray-300 rounded p-2 text-sm focus:ring-2 focus:ring-indigo-500 focus:outline-none" />
                          <button type="button" @click="removeCustomAttribute(variant, attrIdx)" class="text-gray-400 hover:text-red-500" title="Удалить">✕</button>
                        </div>
                      </div>
                    </div>

                  </div>

                  <div>
                    <div class="flex justify-between items-end mb-1">
                      <label class="block text-sm font-medium">Список ключей (каждый с новой строки)</label>
                      <span class="text-xs font-medium text-indigo-600 bg-indigo-50 px-2 py-1 rounded">
                        Распознано: {{ countKeys(variant.rawKeys) }} шт.
                      </span>
                    </div>
                    <textarea
                      v-model="variant.rawKeys"
                      rows="4"
                      placeholder="XXXX-YYYY-ZZZZ&#10;AAAA-BBBB-CCCC"
                      class="w-full border border-gray-300 rounded-lg p-3 font-mono text-sm focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                    ></textarea>
                  </div>
                </div>
              </div>
            </section>

            <div class="flex justify-end pt-6 border-t mt-8">
              <button type="submit" class="bg-indigo-600 text-white px-8 py-3 rounded-lg font-medium hover:bg-indigo-700 transition shadow-md">
                Опубликовать товар
              </button>
            </div>

          </form>
        </div>
      </div>

    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'

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
      if (currentUser.value?.role !== 'seller') {
        return navigateTo('/')
      }
    }
  ]
})

const toast = useToast()
const { $api } = useNuxtApp()

// Состояния
const currentView = ref('list')
const products = ref([])
const categories = ref([])
const imageFile = ref(null)
const selectedCategoryData = ref(null) // Подробные данные выбранной категории

// Вычисляем строгие фильтры из выбранной категории
const strictFilters = computed(() => {
  if (!selectedCategoryData.value?.filter_config) return []
  return selectedCategoryData.value.filter_config.filter(f => f.strict_options)
})

// Базовая инициализация системных атрибутов для варианта
const buildDefaultSystemAttributes = () => {
  const attrs = {}
  strictFilters.value.forEach(f => {
    // Если это чекбокс (множественный выбор), инициализируем массив. Иначе - пустую строку.
    attrs[f.key] = f.type === 'checkbox' ? [] : ''
  })
  return attrs
}

// Загрузка товаров
const fetchProducts = async () => {
  try {
    products.value = await $api('/api/seller/products')
  } catch (error) {
    toast.add({ title: 'Ошибка', description: 'Не удалось загрузить товары', color: 'red' })
  }
}

// Загрузка списка категорий
const fetchCategories = async () => {
  try {
    categories.value = await $api('/api/seller/categories')
  } catch (error) {
    toast.add({ title: 'Ошибка', description: 'Не удалось загрузить категории', color: 'red' })
  }
}

// Подгрузка деталей категории (чтобы вытащить filter_config) при смене селекта
const onCategoryChange = async () => {
  if (!form.value.category_id) return

  try {
    // 1. Находим выбранную категорию в загруженном массиве
    const selectedCat = categories.value.find(c => c.id === form.value.category_id)

    // 2. Достаем slug (если по какой-то причине его нет, ставим заглушку 'catalog')
    const slug = selectedCat?.slug || 'catalog'

    // 3. Делаем правильный запрос
    selectedCategoryData.value = await $api(`/api/categories/${slug}/${form.value.category_id}`)

    // Перестраиваем системные атрибуты у всех существующих вариантов в форме
    form.value.variants.forEach(variant => {
      variant.systemAttributes = buildDefaultSystemAttributes()
    })
  } catch (error) {
    toast.add({ title: 'Ошибка', description: 'Не удалось загрузить фильтры категории', color: 'red' })
  }
}

onMounted(() => {
  fetchProducts()
  fetchCategories()
})

const onFileChange = (event) => {
  const file = event.target.files?.[0] || null
  imageFile.value = file
}

// Сброс формы (теперь с разделением атрибутов)
const resetForm = () => {
  imageFile.value = null
  selectedCategoryData.value = null
  return {
    title: '',
    description: '',
    category_id: '',
    variants: [{
      price: null,
      systemAttributes: {},
      customAttributes: [{ key: '', value: '' }],
      rawKeys: ''
    }]
  }
}

const form = ref(resetForm())

const addVariant = () => {
  form.value.variants.push({
    price: null,
    systemAttributes: buildDefaultSystemAttributes(), // сразу добавляем актуальные системные поля
    customAttributes: [{ key: '', value: '' }],
    rawKeys: ''
  })
}
const removeVariant = (index) => form.value.variants.splice(index, 1)

const addCustomAttribute = (variant) => variant.customAttributes.push({ key: '', value: '' })
const removeCustomAttribute = (variant, index) => variant.customAttributes.splice(index, 1)

const countKeys = (rawText) => rawText ? rawText.split('\n').filter(k => k.trim()).length : 0

const submitProduct = async () => {
  if (!imageFile.value) {
    toast.add({ title: 'Ошибка', description: 'Пожалуйста, загрузите изображение товара', color: 'red' })
    return
  }

  // Небольшая клиентская валидация системных атрибутов
  for (const v of form.value.variants) {
    for (const f of strictFilters.value) {
      const val = v.systemAttributes[f.key]
      if (!val || (Array.isArray(val) && val.length === 0)) {
        toast.add({ title: 'Ошибка', description: `Заполните обязательное поле: ${f.label}`, color: 'red' })
        return
      }
    }
  }

  try {
    const payload = {
      title: form.value.title,
      description: form.value.description,
      category_id: form.value.category_id,
      variants: form.value.variants.map(v => {
        // 1. Копируем системные атрибуты (выбранные галочки и селекты)
        const finalAttributes = { ...v.systemAttributes }

        // 2. Добавляем валидные кастомные атрибуты поверх системных
        v.customAttributes.forEach(attr => {
          if (attr.key.trim() && attr.value.trim()) {
            finalAttributes[attr.key.trim()] = attr.value.trim()
          }
        })

        return {
          price: v.price,
          attributes: Object.keys(finalAttributes).length ? finalAttributes : null,
          items: v.rawKeys
            .split('\n')
            .map(k => k.trim())
            .filter(Boolean)
            .map(content => ({ content }))
        }
      })
    }

    const formData = new FormData()
    formData.append('data', JSON.stringify(payload))
    formData.append('file', imageFile.value)

    await $api('/api/seller/products', {
      method: 'POST',
      body: formData
    })

    toast.add({ title: 'Успешно', description: 'Товар сохранен и опубликован', color: 'green' })

    currentView.value = 'list'
    form.value = resetForm()
    fetchProducts()

  } catch (error) {
    const errorMsg = error.data?.detail || error.response?._data?.detail || 'Ошибка сохранения'
    toast.add({ title: 'Ошибка', description: errorMsg, color: 'red' })
  }
}

useHead({ title: 'Кабинет продавца | myMarket' })
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
