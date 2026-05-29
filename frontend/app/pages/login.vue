<template>
  <UContainer class="flex items-center justify-center min-h-[calc(100vh-64px)]">
    <UCard class="w-full max-w-md shadow-xl" :ui="{ ring: '', divide: 'divide-y divide-gray-100 dark:divide-gray-800' }">
      <template #header>
        <div class="flex items-center justify-center">
          <h3 class="text-xl font-bold text-primary">Добро пожаловать</h3>
        </div>
      </template>

      <UTabs :items="tabs" class="w-full">

        <template #login>
          <form @submit.prevent="handleLogin" class="space-y-4 mt-4">
            <UFormGroup label="Логин">
              <UInput v-model="loginForm.username" type="text" placeholder="Введите логин" icon="i-heroicons-user" />
            </UFormGroup>

            <UFormGroup label="Пароль">
              <UInput v-model="loginForm.password" type="password" placeholder="••••••••" icon="i-heroicons-lock-closed" />
            </UFormGroup>

            <UButton type="submit" color="primary" block>Войти</UButton>
          </form>
        </template>

        <template #register>
          <form @submit.prevent="handleRegister" class="space-y-4 mt-4">
            <UFormGroup label="Я хочу:">
              <URadioGroup v-model="registerForm.role" :options="roleOptions" />
            </UFormGroup>

            <UFormGroup label="Логин">
              <UInput v-model="registerForm.username" type="text" placeholder="Придумайте логин" icon="i-heroicons-user" />
            </UFormGroup>

            <UFormGroup label="Пароль">
              <UInput v-model="registerForm.password" type="password" placeholder="••••••••" icon="i-heroicons-lock-closed" />
            </UFormGroup>

            <UButton type="submit" color="primary" block>Зарегистрироваться</UButton>
          </form>
        </template>

      </UTabs>
    </UCard>
  </UContainer>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const config = useRuntimeConfig()
const router = useRouter()
const toast = useToast()

const currentUser = useState('user', () => null)

const tabs = [
  { slot: 'login', label: 'Вход' },
  { slot: 'register', label: 'Регистрация' }
]

const roleOptions = [
  { value: 'client', label: 'Покупать товары' },
  { value: 'seller', label: 'Продавать товары' }
]

const loginForm = ref({ username: '', password: '' })
const registerForm = ref({ role: 'client', username: '', password: '' })

const onAuthSuccess = (user, successMessage) => {
  currentUser.value = user
  toast.add({ title: 'Успешно', description: successMessage, color: 'green' })
  router.push(user.role === 'seller' ? '/seller' : '/catalog')
}

const handleLogin = async () => {
  try {
    const authResponse = await $fetch(`${config.public.apiBase}/api/login`, {
      method: 'POST',
      body: loginForm.value,
      credentials: 'include'
    })

    if (authResponse.user) {
      onAuthSuccess(authResponse.user, 'Вы вошли в аккаунт')
    }
  } catch (error) {
    const errorMsg = error.response?._data?.detail || 'Ошибка соединения с сервером'
    toast.add({ title: 'Ошибка входа', description: errorMsg, color: 'red' })
  }
}

const handleRegister = async () => {
  try {
    const authResponse = await $fetch(`${config.public.apiBase}/api/register`, {
      method: 'POST',
      body: registerForm.value,
      credentials: 'include'
    })

    if (authResponse.user) {
      onAuthSuccess(authResponse.user, 'Вы автоматически вошли в аккаунт.')
    }
  } catch (error) {
    const errorMsg = error.response?._data?.detail || 'Ошибка регистрации'
    toast.add({ title: 'Ошибка', description: errorMsg, color: 'red' })
  }
}

useHead({ title: 'Вход в аккаунт | myMarket' })
</script>
