Default.vue
<template>
 <v-app :theme="theme">
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
   theme: 'dark'
 }),
 head: {
   title: 'Recipes'
 },
}
</script>
