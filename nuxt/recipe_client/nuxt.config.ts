// https://nuxt.com/docs/api/configuration/nuxt-config
import vuetify, { transformAssetUrls } from 'vite-plugin-vuetify'
export default defineNuxtConfig({
  compatibilityDate: '2025-05-15',
  ssr: false,
  devtools: {
    enabled: true,

    timeline: {
      enabled: true,
    },
  },
  runtimeConfig: {
    public: {
      baseURL: process.env.API_BASE
    }
  },
  routeRules: {
    '/recipes/**': { ssr: false }
  },
  plugins: [
    '~/plugins/auth.ts',
  ],
  build: {
    transpile: ['vuetify'],
  },
  modules: [
    '@nuxt/eslint',
    (_options, nuxt) => {
      nuxt.hooks.hook('vite:extendConfig', (config) => {
        // @ts-expect-error
        config.plugins.push(vuetify({ autoImport: true }))
      })
    },
    '@vueuse/nuxt',
    '@nuxt/eslint'
  ],
  vite: {
    vue: {
      template: {
        transformAssetUrls,
      },
    },
  },
})