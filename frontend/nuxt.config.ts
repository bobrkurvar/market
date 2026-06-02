// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  modules: [
    '@nuxt/eslint',
    '@nuxt/ui'
  ],
  devtools: {
    enabled: true
  },
  ssr: false,
  css: ['~/assets/css/main.css'],

  routeRules: {
    '/': { prerender: true }
  },
  runtimeConfig: {
    public: {
      apiBase: '/api'
    }
  },

  colorMode: {
    preference: 'dark', // Жестко ставим темную
    fallback: 'dark',
    classSuffix: ''     // Важно для совместимости с Tailwind
  },

  compatibilityDate: '2025-01-15',

  eslint: {
    config: {
      stylistic: {
        commaDangle: 'never',
        braceStyle: '1tbs'
      }
    }
  }
})
