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
            <UFormField label="Логин" name="username">
              <UInput v-model="loginForm.username" type="text" placeholder="Введите логин" icon="i-heroicons-user" />
            </UFormField>

            <UFormField label="Пароль" name="password">
              <UInput v-model="loginForm.password" type="password" placeholder="••••••••" icon="i-heroicons-lock-closed" />
            </UFormField>

            <UButton type="submit" color="primary" block>Войти</UButton>
          </form>
        </template>

        <template #register>
          <form @submit.prevent="handleRegister" class="space-y-4 mt-4">

            <UFormField label="Тип аккаунта" name="role">
              <URadioGroup
                v-model="registerForm.role"
                :items="roleOptions"
                class="mt-2"
              />
            </UFormField>

            <UFormField label="Логин" name="username">
              <UInput v-model="registerForm.username" type="text" placeholder="Придумайте логин" icon="i-heroicons-user" />
            </UFormField>

            <UFormField label="Пароль" name="password">
              <UInput v-model="registerForm.password" type="password" placeholder="••••••••" icon="i-heroicons-lock-closed" />
            </UFormField>

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

const router = useRouter()
const toast = useToast()
const { $api } = useNuxtApp()

const currentUser = useState('user', () => null)

const tabs = [
  { slot: 'login', label: 'Вход' },
  { slot: 'register', label: 'Регистрация' }
]

const roleOptions = [
  { value: 'user', label: 'Покупать товары' },
  { value: 'seller', label: 'Продавать товары' }
]

const loginForm = ref({ username: '', password: '' })
const registerForm = ref({ role: 'user', username: '', password: '' })

const onAuthSuccess = (user, successMessage) => {
  currentUser.value = user
  toast.add({ title: 'Успешно', description: successMessage, color: 'green' })
  router.push('/')
}

const handleLogin = async () => {
  try {
    const authResponse = await $api('/api/login', {
      method: 'POST',
      body: loginForm.value
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
    const authResponse = await $api('/api/register', {
      method: 'POST',
      body: registerForm.value
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
