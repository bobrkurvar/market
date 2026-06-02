import { defineNuxtPlugin, useState } from '#app'

let refreshPromise: Promise<any> | null = null;

export default defineNuxtPlugin((nuxtApp) => {
  const config = useRuntimeConfig()

  const api = $fetch.create({
    baseURL: config.public.apiBase as string,
    credentials: 'include',

    async onResponseError({ request, response, options }) {
      if (response.status === 401) {

        // Если сам рефреш вернул 401 (токен протух или его нет)
        if (request.toString().endsWith('/refresh')) {
          const currentUser = useState('user')
          currentUser.value = null
          refreshPromise = null
          // НЕ редиректим, а просто возвращаем ошибку,
          // чтобы вызов $api('/api/me') завершился провалом
          throw new Error('Refresh failed')
        }

        if (!refreshPromise) {
          refreshPromise = $fetch(`${config.public.apiBase}/refresh`, {
            method: 'POST',
            credentials: 'include',
            retry: 0
          }).finally(() => {
            refreshPromise = null
          })
        }

        try {
          await refreshPromise
          // Повторяем оригинальный запрос
          return $fetch(request, options)
        } catch (error) {
          // Если очередь рефрешей упала
          const currentUser = useState('user')
          currentUser.value = null
          // Тоже пробрасываем ошибку дальше
          throw error
        }
      }
    }
  })

  return { provide: { api } }
})
