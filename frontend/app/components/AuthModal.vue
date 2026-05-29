<template>
  <UModal v-model="isOpen">
    <UCard :ui="{ ring: '', divide: 'divide-y divide-gray-100 dark:divide-gray-800' }">
      <template #header>
        <div class="flex items-center justify-between">
          <h3 class="text-lg font-semibold">Личный кабинет</h3>
          <UButton color="gray" variant="ghost" icon="i-heroicons-x-mark-20-solid" class="-my-1" @click="closeModal" />
        </div>
      </template>

      <UTabs :items="tabs" class="w-full">

        <template #login>
          <form @submit.prevent="handleLogin" class="space-y-4 mt-4">
            <UFormGroup label="Email">
              <UInput v-model="loginForm.email" type="email" placeholder="you@example.com" icon="i-heroicons-envelope" />
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

            <UFormGroup label="Имя / Название магазина">
              <UInput v-model="registerForm.name" placeholder="Как к вам обращаться?" icon="i-heroicons-user" />
            </UFormGroup>

            <UFormGroup label="Email">
              <UInput v-model="registerForm.email" type="email" placeholder="you@example.com" icon="i-heroicons-envelope" />
            </UFormGroup>

            <UFormGroup label="Пароль">
              <UInput v-model="registerForm.password" type="password" placeholder="••••••••" icon="i-heroicons-lock-closed" />
            </UFormGroup>

            <UButton type="submit" color="green" block>Зарегистрироваться</UButton>
          </form>
        </template>

      </UTabs>
    </UCard>
  </UModal>
</template>

<script setup>
import { ref } from 'vue'

// Подключаем наш глобальный стейт
const { isOpen, closeModal } = useAuthModal()

// Настройки вкладок
const tabs = [
  { slot: 'login', label: 'Вход' },
  { slot: 'register', label: 'Регистрация' }
]

// Варианты ролей при регистрации
const roleOptions = [
  { value: 'client', label: 'Покупать товары' },
  { value: 'seller', label: 'Продавать товары' }
]

// Данные форм
const loginForm = ref({
  email: '',
  password: ''
})

const registerForm = ref({
  role: 'client',
  name: '',
  email: '',
  password: ''
})

// Заглушки функций для отправки на бэк
const handleLogin = async () => {
  console.log('Отправляем на бэк запрос на ВХОД:', loginForm.value)
  // Тут будет запрос к FastAPI
}

const handleRegister = async () => {
  console.log('Отправляем на бэк запрос на РЕГИСТРАЦИЮ:', registerForm.value)
  // Тут будет запрос к FastAPI
}
</script>
