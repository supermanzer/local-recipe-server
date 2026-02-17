<template>
    <v-card>
        <v-card-title>Ingredients</v-card-title>

        <v-list
        >
            <v-list-item
            v-for="(ingredient, index) in props.modelValue"
            :key="index"
            >
                <v-row>
                    <v-col>
                        <v-combobox
                        :model-value="ingredient.name"
                        label="Ingredient name"
                        :items="options"
                        item-title="name"
                        item-value="name"
                        density="compact"
                        @update:model-value="(value) => updateIngredientName(index, value)"
                        />
                    </v-col>
                    <v-col>
                        <v-text-field
                          v-model="ingredient.amount"
                          label = "Amount"
                          density="compact"
                        />
                    </v-col>
                    <v-col>
                        <v-text-field
                          v-model="ingredient.unit"
                          label = "Unit"
                          density="compact"
                        />
                    </v-col>
                    <v-col cols="12" sm="1">
                        <v-tooltip text="Remove ingredient">
                            <template #activator="{props: delProps}">
                                <v-btn variant="outlined" v-bind="delProps" color="red-darken-1" icon="mdi-minus" @click="removeIngredient(index)"/>
                            </template>
                        </v-tooltip>
                    </v-col>
                </v-row>
            </v-list-item>
        </v-list>
        <v-divider/>

        <v-card-actions>
            <v-row class="my-6 px-10" justify="end">
                <v-tooltip text="Add Ingredient">
                    <template #activator="{props: addProps}">
                        <v-btn v-bind="addProps" variant="outlined" color="green" icon="mdi-plus" @click="addIngredient"/>
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

const props = defineProps<{modelValue: Ingredient[], options: Ingredient[]}>();
const emit = defineEmits(['update:modelValue']);

const updateIngredientName = (index: number, value: any) => {
    // Extract name if value is an object, otherwise use value as-is
    const name = typeof value === 'object' && value !== null && value.name ? value.name : value;
    const updated = [...props.modelValue];
    updated[index].name = name;
    emit('update:modelValue', updated);
};

const addIngredient = () => {
    emit('update:modelValue', [...props.modelValue, {name: '', amount: 0, unit: ''}])
}

const removeIngredient = (index: number) => {
    emit('update:modelValue', props.modelValue.filter((_, i) => i !== index));
};

</script>