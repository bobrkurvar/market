<template>
  <div class="min-h-screen bg-background text-foreground antialiased font-sans">

    <AppHeader />

    <main>
      <slot />
    </main>

    <UNotifications />
  </div>
</template>

<script setup>
const router = useRouter()
const currentUser = useState('user')
const colorMode = useColorMode()

const dropdownItems = [
  [{
    label: 'Панель управления',
    icon: 'i-heroicons-cog-8-tooth',
    click: () => {
       const path = currentUser.value.role === 'seller' ? '/seller' : '/profile'
       router.push(path)
    }
  }],
  [{
    label: 'Выйти',
    icon: 'i-heroicons-arrow-right-on-rectangle',
    click: () => {
      currentUser.value = null
      router.push('/catalog')
    }
  }]
]
</script>
