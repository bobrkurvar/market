export default defineNuxtPlugin((nuxtApp) => {
  const config = useRuntimeConfig()

  // Создаем инстанс с указанием базового URL
  const api = $fetch.create({
    baseURL: config.public.apiBase as string,
    credentials: 'include',

    async onResponseError({ request, response, options }) {
      if (response.status === 401) {

        // Защита от мертвой петли рефреша
        if (request.toString().endsWith('/api/refresh')) {
          const currentUser = useState('user')
          currentUser.value = null
          return navigateTo('/')
        }

        try {
          // Запрашиваем обновление кук
          await $fetch(`${config.public.apiBase}/api/refresh`, {
            method: 'POST',
            credentials: 'include'
          })

          // Повторяем оригинальный запрос
          return $fetch(request, options)

        } catch (error) {
          // Если refresh упал с ошибкой
          const currentUser = useState('user')
          currentUser.value = null
          return navigateTo('/')
        }
      }
    }
  })

  return {
    provide: {
      api
    }
  }
})
