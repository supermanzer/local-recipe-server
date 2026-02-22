<template>
    <v-row class="my-2" justify="space-around"> 
        <v-combobox
            v-if="ingredients"
            v-model="state.ingrediengs"
            :items="ingredients"
            item-title="name"
            item-value="id"
            multiple
            label="Search Ingredients"
            variant="underlined"
            chips
            clearable
            prepend-icon="mdi-magnify"
            @update:model-value="selectIngredient"
        />
        <v-tooltip text="Create new recipe">
            <template #activator="{props}">
                <v-btn
                    v-bind="props"
                    icon="mdi-plus"
                    color="green-darken-3"
                    class="mx-4"
                    to="recipes/new"
                />
            </template>
        </v-tooltip>
    </v-row>
</template>

<script setup lang="js">
const {getIngredients} = recipeUtils();
const emits = defineEmits(['ingedientSelected'])

const state = reactive({
    ingrediengs: []
})
const {data: ingredients, error} = await useAsyncData('ingredients',() => getIngredients());

if (error) {
    console.error(error)
}

const selectIngredient = () => {
    const ingredient_ids = state.ingrediengs.map((o) => o.id);
    const inredient_names = state.ingrediengs.map((o) => o.name);
    const data = {
        ids: ingredient_ids,
        names: inredient_names
    }
    emits('ingedientSelected', data)
}

</script>