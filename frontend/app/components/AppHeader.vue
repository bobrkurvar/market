<template>
  <header class="sticky top-0 z-50 backdrop-blur-md bg-slate-950/70 border-b border-gray-100/10">
    <UContainer class="flex items-center justify-between h-16">

      <div class="text-xl font-black tracking-wider text-primary-500 cursor-pointer flex items-center gap-1" @click="$router.push('/')">
        my<span class="text-white">Market</span>
      </div>

      <nav class="hidden md:flex space-x-6">
        <NuxtLink to="/catalog" class="text-sm font-medium text-gray-300 hover:text-primary-400 transition-colors">
          Каталог
        </NuxtLink>
      </nav>

      <div class="flex items-center gap-3">

        <UButton
          :icon="colorMode.value === 'dark' ? 'i-heroicons-sun-20-solid' : 'i-heroicons-moon-20-solid'"
          color="neutral"
          variant="ghost"
          aria-label="Theme"
          @click="colorMode.preference = colorMode.value === 'dark' ? 'light' : 'dark'"
        />

        <UButton v-if="!currentUser" to="/login" color="neutral" variant="subtle" class="font-medium px-4">
          Войти
        </UButton>

        <UDropdownMenu v-else :items="dropdownItems">
          <UButton color="neutral" variant="ghost" class="text-gray-200 hover:bg-slate-900" trailing-icon="i-heroicons-chevron-down-20-solid">
            <UAvatar :alt="currentUser.username" size="xs" class="mr-1 bg-primary-500 text-white font-bold" />
            {{ currentUser.username }}
            <span class="text-xs text-gray-400 ml-1">({{ currentUser.role === 'seller' ? 'Продавец' : 'Клиент' }})</span>
          </UButton>
        </UDropdownMenu>
      </div>

    </UContainer>
  </header>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()
const currentUser = useState('user')
const colorMode = useColorMode()
const { $api } = useNuxtApp()

const dropdownItems = [
  [{
    label: 'Панель управления',
    icon: 'i-heroicons-cog-8-tooth',
    // В Nuxt UI v4 клик по меню обрабатывается через onSelect
    onSelect: () => {
       const path = currentUser.value.role === 'seller' ? '/seller' : '/profile'
       router.push(path)
    }
  }],
  [{
    label: 'Выйти',
    icon: 'i-heroicons-arrow-right-on-rectangle',
    onSelect: async () => {
      try {
        await $api('/api/logout', { method: 'POST' })
      } catch (e) {} // Игнорируем ошибку при выходе
      currentUser.value = null
      router.push('/catalog')
    }
  }]
]
</script>
