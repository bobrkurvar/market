<template>
  <NuxtLayout>
    <NuxtPage />
  </NuxtLayout>
</template>

<script setup>
const config = useRuntimeConfig()
const currentUser = useState('user', () => null)

const { data, refresh } = await useFetch(`${config.public.apiBase}/api/me`, {
  credentials: 'include',
  server: false,
})


watch(data, (newData) => {
  if (newData?.user) {
    currentUser.value = newData.user
  } else {
    currentUser.value = null
  }
}, { immediate: true })
</script>
