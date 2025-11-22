<template>
    <v-list-item :class="{ 'highlighted': isHighlighted }">
        <v-list-item-title class="text-wrap" :class="{ 'font-weight-bold': isHighlighted }" v-text="itemTitle"></v-list-item-title>
        <template v-if="isHighlighted" v-slot:append>
            <v-icon icon="mdi-check-circle" color="success"></v-icon>
        </template>
    </v-list-item>
</template>

<script setup lang="js">
const { ingredient, highlightedIds } = defineProps({
    ingredient: { type: Object, required: false, default: () => {} },
    highlightedIds: { type: Array, required: false, default: () => [] }
})

const itemTitle = computed(() => `${ingredient.amount} ${ingredient.unit} ${ingredient.name}`)

const isHighlighted = computed(() => highlightedIds.includes(ingredient.id))
</script>

<style scoped>
.highlighted {
    background-color: rgba(76, 175, 80, 0.1);
    transition: background-color 0.2s ease;
}

.highlighted :deep(.v-list-item__content) {
    color: rgb(56, 142, 60);
}
</style>