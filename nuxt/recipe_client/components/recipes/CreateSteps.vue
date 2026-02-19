<template>
    <v-card>
        <v-card-title>Steps</v-card-title>
        <v-card-text>
            <v-list>
                <RecipesStepItem
                    v-for="(step, index) in modelValue"
                    :key="index"
                    :step="step"
                    :ingredients="ingredients"
                    @update:step="updateStep(index, $event)"
                    @delete="removeStep(index)"
                />
            </v-list>
        </v-card-text>
        <v-card-actions>
            <v-row class="my-6 px-10" justify="end">
                <v-tooltip text="Add Step">
                    <template #activator="{props: addProps}">
                        <v-btn v-bind="addProps" variant="outlined" color="green" icon="mdi-plus" @click="addStep"/>
                    </template>
                </v-tooltip>
            </v-row>
        </v-card-actions>
    </v-card>
</template>

<script setup lang="ts">
import type { RecipeStepInput, RecipeIngredientInput } from '~/types/recipe.types'

const props = defineProps<{
    modelValue: RecipeStepInput[]
    ingredients: RecipeIngredientInput[]
}>()

const emit = defineEmits<{
    'update:modelValue': [steps: RecipeStepInput[]]
}>()

/**
 * Update a specific step in the array
 * Called when StepItem emits an update
 */
const updateStep = (index: number, updatedStep: RecipeStepInput) => {
    const updated = [...props.modelValue]
    updated[index] = updatedStep
    emit('update:modelValue', updated)
}

/**
 * Add a new step with the next available order number
 */
const addStep = () => {
    const newOrder = Math.max(...props.modelValue.map(s => s.order), 0) + 1
    emit('update:modelValue', [
        ...props.modelValue,
        { order: newOrder, step: '', ingredients: [] }
    ])
}

/**
 * Remove a step at the specified index
 */
const removeStep = (index: number) => {
    emit('update:modelValue', props.modelValue.filter((_, i) => i !== index))
}
</script>