<template>
    <tr class="text-no-wrap">
        <td>{{ item.name }}</td>
        <td>{{ remainingIngredients }}</td>
        <td>
            <v-tooltip text="Go to recipe">
                <template #activator="{ props}">
                    <v-icon 
                        v-bind="props"
                        color="green-darken-4"
                        icon="mdi-link-variant"
                        @click="goToRecipe(item.id)"
                    />
                </template>
            </v-tooltip>
        </td>
    </tr>
</template>

<script setup lang="ts">
import type { Recipe } from '~/types/recipe.types';

const { goToRecipe } = recipeUtils()

const {item, selectedIngredients} = defineProps({
    item: {type: Object as PropType<Recipe>, required: false, default: () => ({})},
    selectedIngredients: {type: Array, required: false, default: () => []}
})
const remainingIngredients = computed(() => {
    return item.ingredients.filter((o) => !selectedIngredients.includes(o.name)).map(o => o.name).join(', ')
})

</script>