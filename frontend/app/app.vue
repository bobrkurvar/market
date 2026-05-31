<template>
  <div v-if="isCheckingAuth" class="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-950">
    <UIcon name="i-heroicons-arrow-path" class="w-8 h-8 animate-spin text-primary-500" />
  </div>

  <NuxtLayout v-else>
    <NuxtPage />
  </NuxtLayout>
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
    // 1. Делаем запрос за профилем
    const data = await $api('/api/me')
    // 2. Сохраняем стейт
    currentUser.value = data?.user || data
  } catch (error) {
    // 3. Если кук нет или они протухли - очищаем
    currentUser.value = null
  } finally {
    // 4. СНИМАЕМ БЛОКИРОВКУ (только теперь приложение начнет рендериться!)
    isCheckingAuth.value = false
  }
})
</script>
