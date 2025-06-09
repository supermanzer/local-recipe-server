<template>
    <v-list-item>
        <v-list-item-title v-text="itemTitle"></v-list-item-title>
    </v-list-item>
</template>

<script setup lang="js">
    const { ingredient } = defineProps({
        ingredient: {type: Object, required: false, default: () => {}}
    })
    const itemTitle = computed(() => `${ingredient.amount} ${ingredient.unit} ${ingredient.name}`)
</script>