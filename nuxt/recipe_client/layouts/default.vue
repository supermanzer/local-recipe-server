<template>
  <v-app>
    <nav-header></nav-header>
    <v-main>
      <v-container>
        <Nuxt />
      </v-container>
    </v-main>
  </v-app>
</template>

<script>
export default {
  data: () => ({
    theme: 'light',
  }),
  head: {
    title: 'Recipes',
  },
}
</script>
