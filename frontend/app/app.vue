<template>
  <div>
    <div
      v-if="isCheckingAuth"
      class="fixed inset-0 z-50 flex items-center justify-center bg-gray-50 dark:bg-gray-950"
    >
      <UIcon name="i-heroicons-arrow-path" class="w-8 h-8 animate-spin text-primary-500" />
    </div>

    <NuxtLayout>
      <NuxtPage />
    </NuxtLayout>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const { $api } = useNuxtApp()
const currentUser = useState('user')

// Ставим жесткую блокировку по умолчанию
const isCheckingAuth = ref(true)

// onMounted выполняется ТОЛЬКО в браузере клиента, где уже есть куки
onMounted(async () => {
  try {
    // 1. Делаем запрос за профилем.
    // Если мы гость, плагин api.ts выкинет ошибку (throw), и мы попадем в catch
    const data = await $api('/api/me')
    currentUser.value = data?.user || data
  } catch (error) {
    // 2. Срабатывает при 401 ошибке от бэкенда. Просто обнуляем стейт.
    currentUser.value = null
  } finally {
    // 3. Убираем "шторку" лоадера
    isCheckingAuth.value = false
  }
})
</script>
