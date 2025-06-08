<template>
    <v-container>
        <p class="text-h1">Recipes</p>
    </v-container>
</template>

<script setup lang="js">
    const config = useRuntimeConfig();
    const stuff = await useFetch('/recipes/', {baseURL: config.public.baseURL})    
</script>