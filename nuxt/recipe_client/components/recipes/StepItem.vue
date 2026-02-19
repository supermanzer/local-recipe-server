<template>
    <v-list-item>
        <v-row>
            <v-col cols="1">
                <v-text-field
                    :model-value="step.order"
                    label="Step #"
                    type="number"
                    min="1"
                    density="compact"
                    @update:model-value="updateOrder"
                />
            </v-col>
            <v-col cols="5">
                <v-textarea
                    :model-value="step.step"
                    label="Step Instructions"
                    rows="3"
                    density="compact"
                    @update:model-value="updateStepText"
                />
            </v-col>
            <v-col cols="5">
                <v-autocomplete
                    v-model="selectedIngredients"
                    :items="ingredientOptions"
                    label="Ingredients for this step"
                    multiple
                    chips
                    closable-chips
                    density="compact"
                    @update:model-value="updateIngredients"
                />
            </v-col>
            <v-col cols="1">
                <v-btn
                    icon="mdi-minus"
                    variant="outlined"
                    color="error"
                    size="small"
                    @click="$emit('delete')"
                />
            </v-col>
        </v-row>
    </v-list-item>
</template>

<script setup lang="ts">
import type { RecipeStepInput, RecipeIngredientInput } from '~/types/recipe.types'

interface Props {
    step: RecipeStepInput
    ingredients: RecipeIngredientInput[]
}

const props = defineProps<Props>()

const emit = defineEmits<{
    'update:step': [step: RecipeStepInput]
    'delete': []
}>()

// Local state for selected ingredients (array of indices)
const selectedIngredients = ref<number[]>(
    props.step.ingredients.map(ing => ing.ingredient_index)
)

// Watch for external changes (e.g., when loading a recipe)
// This syncs selectedIngredients when the step prop changes
watch(
    () => props.step.ingredients,
    (newIngredients) => {
        selectedIngredients.value = newIngredients.map(ing => ing.ingredient_index)
    },
    { deep: true }
)

// Computed options for autocomplete
const ingredientOptions = computed(() =>
    props.ingredients.map((ing, idx) => ({
        title: `${ing.name} (${ing.amount} ${ing.unit})`,
        value: idx
    }))
)

// Emit updated step when order changes
const updateOrder = (newOrder: string) => {
    const newOrderInt = Number(newOrder)
    emit('update:step', {
        ...props.step,
        order: newOrderInt
    })
}

// Emit updated step when step text changes
const updateStepText = (newText: string) => {
    emit('update:step', {
        ...props.step,
        step: newText
    })
}

// Emit updated step when ingredients selection changes
const updateIngredients = (selectedIndices: number[]) => {
    emit('update:step', {
        ...props.step,
        ingredients: selectedIndices.map(idx => ({
            ingredient_index: idx
        }))
    })
}
</script>
