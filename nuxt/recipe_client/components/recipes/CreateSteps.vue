<template>
    <v-card>
        <v-card-title>Steps</v-card-title>
        <v-card-text>
            <v-list>
                <v-list-item v-for="(step, index) in modelValue" :key="index">
                    <v-row>
                        <v-col cols="12" sm="1">
                            <v-text-field
                              v-model.number="step.order"
                              label="Order"
                              placeholder="1"
                            />
                        </v-col>
                        <v-textarea
                          v-model="step.step"
                          label="Step Instructions"
                          counter
                          max-length="1000"
                        />
                        <!-- Ingredient Selection -->
                         <v-col>
                             <v-autocomplete
                               v-model="selectedIngredients[index]"
                               :items="ingredientOptions"
                               item-title="title"
                               item-value="value"
                               label="Ingredients used in this step"
                               multiple
                               chips
                               @update:model-value="updateStepIngredient(index, $event)"
                             />
                         </v-col>
                         <v-col cols="12" sm="1">
                            <v-tooltip text="Remove Step">
                                <template #activator="{props: delProps}">
                                    <v-btn variant="outlined" v-bind="delProps" color="red-darken-1" icon="mdi-minus" @click="removeStep(index)"/>
                                </template>
                            </v-tooltip>
                         </v-col>
                    </v-row>
                </v-list-item>
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
interface Ingredient {
    name: string;
    amount: number | string;
    unit: string;
}

interface Step {
    order: number;
    step: string;
    ingredients: Array<{ingredient_index: number}>
}

const props = defineProps<{modelValue: Step[]; ingredients: Ingredient[]}>();
const emit = defineEmits(['update:modelValue']);

const selectedIngredients = ref<number[][]>(
    props.modelValue.map(step => 
        step.ingredients.map(ing => ing.ingredient_index)
    )
)

const ingredientOptions = computed(() => 
    props.ingredients.map((ing, idx) => ({
        title: `${ing.name} (${ing.amount}, ${ing.unit})`,
        value: idx
    })
))

const updateStepIngredient = (stepIndex: number, ingredientIndices:  number[]) => {
    const updated = [...props.modelValue];
    updated[stepIndex].ingredients = ingredientIndices.map(idx => ({
        ingredient_index: idx
    }));
    emit('update:modelValue', updated)
}

const addStep = () => {
    const newOrder = Math.max(...props.modelValue.map(s => s.order), 0) + 1;
    emit('update:modelValue', [
        ...props.modelValue,
        {order: newOrder, step: '', ingredients: []}
    ]);
}

const removeStep = (index: number) => {
    emit('update:modelValue', props.modelValue.filter((_, i) => i !== index));
}
</script>