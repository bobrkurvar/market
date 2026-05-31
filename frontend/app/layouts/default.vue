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
</script>
