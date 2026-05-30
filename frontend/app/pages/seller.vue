<template>
  <div class="min-h-screen bg-gray-50 font-sans">
    <main class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">

      <div v-if="currentView === 'list'" class="space-y-6">

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
                    {{ product.items_available }} шт.
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

      <div v-else-if="currentView === 'create'" class="max-w-4xl mx-auto">

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
                  <label class="block text-sm font-medium mb-1">Описание</label>
                  <textarea v-model="form.description" rows="3" placeholder="Подробное описание товара..." class="w-full border border-gray-300 rounded-lg p-3 focus:ring-2 focus:ring-indigo-500 focus:outline-none"></textarea>
                </div>
              </div>
            </section>

            <section>
              <div class="flex justify-between items-center mb-4 border-b pb-2">
                <h3 class="text-lg font-semibold">Опции и ключи</h3>
                <button type="button" @click="addVariant" class="text-indigo-600 hover:underline text-sm font-medium flex items-center">
                  <span>+ Добавить опцию</span>
                </button>
              </div>

              <div class="space-y-6">
                <div v-for="(variant, index) in form.variants" :key="index" class="bg-gray-50 p-6 rounded-lg border border-gray-200 relative group">

                  <button v-if="form.variants.length > 1" type="button" @click="removeVariant(index)" class="absolute top-4 right-4 text-gray-400 hover:text-red-500 transition opacity-0 group-hover:opacity-100" title="Удалить опцию">
                    ✕
                  </button>

                  <h4 class="font-medium text-gray-700 mb-4">Опция #{{ index + 1 }}</h4>

                  <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                    <div>
                      <label class="block text-sm font-medium mb-1">Цена (₽) <span class="text-red-500">*</span></label>
                      <input v-model.number="variant.price" type="number" min="0" required class="w-full border border-gray-300 rounded-lg p-3 focus:ring-2 focus:ring-indigo-500 focus:outline-none" />
                    </div>
                    <div>
                      <label class="block text-sm font-medium mb-1">Характеристика (напр. 1 месяц)</label>
                      <input v-model="variant.durationAttr" type="text" placeholder="Укажите длительность или тип" class="w-full border border-gray-300 rounded-lg p-3 focus:ring-2 focus:ring-indigo-500 focus:outline-none" />
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
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

definePageMeta({
  middleware: [
    function (to, from) {
      const currentUser = useState('user').value
      if (!currentUser || currentUser.role !== 'seller') {
        return navigateTo('/')
      }
    }
  ]
})

const config = useRuntimeConfig()
const router = useRouter()
const toast = useToast()
const { $api } = useNuxtApp()

const currentUser = useState('user')
const currentView = ref('list')
const products = ref([])

const fetchProducts = async () => {
  try {
    // В реальности: await $api('/api/seller/products')
    products.value = [
      { id: 1, title: 'Подписка Netflix Premium 4K', variants_count: 2, items_available: 45 },
      { id: 2, title: 'Ключ Windows 11 Pro', variants_count: 1, items_available: 12 },
    ]
  } catch (error) {
    console.error('Ошибка загрузки товаров', error)
  }
}

onMounted(() => {
  fetchProducts()
})

const resetForm = () => {
  return {
    title: '',
    description: '',
    variants: [ { price: null, durationAttr: '', rawKeys: '' } ]
  }
}

const form = ref(resetForm())

const addVariant = () => form.value.variants.push({ price: null, durationAttr: '', rawKeys: '' })
const removeVariant = (index) => form.value.variants.splice(index, 1)

const countKeys = (rawText) => {
  if (!rawText) return 0
  return rawText.split('\n').filter(line => line.trim() !== '').length
}

const submitProduct = async () => {
  try {
    const payload = {
      title: form.value.title,
      description: form.value.description,
      variants: form.value.variants.map(v => ({
        price: v.price,
        attributes: v.durationAttr ? { duration: v.durationAttr } : {},
        items: v.rawKeys
          .split('\n')
          .map(k => k.trim())
          .filter(k => k !== '')
          .map(k => ({ content: k }))
      }))
    }

    // В реальности:
    // await $api('/api/product', {
    //   method: 'POST',
    //   body: payload
    // })

    toast.add({ title: 'Успешно', description: 'Товар сохранен и опубликован', color: 'green' })

    currentView.value = 'list'
    form.value = resetForm()
    fetchProducts()

  } catch (error) {
    const errorMsg = error.response?._data?.detail || 'Ошибка сохранения'
    toast.add({ title: 'Ошибка', description: errorMsg, color: 'red' })
  }
}

useHead({ title: 'Кабинет продавца | myMarket' })
</script>
