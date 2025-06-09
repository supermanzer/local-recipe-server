<template>
    <v-data-table
    :headers="headers"
     :items="recipes"
    >
        <template v-slot:item.actions="{item}">
            <div class="d-flex ga-2 justify-end">
                <v-tooltip text="Go to recipe">
                    <template v-slot:activator="{ props}">
                        <v-icon 
                            v-bind="props"
                            color="green-darken-4"
                            icon="mdi-link-variant"
                            @click="goToRecipe(item.id)"
                        />
                    </template>
                </v-tooltip>
            </div>
        </template>
    </v-data-table>
</template>

<script setup lang="js">

const {recipes} = defineProps({
    recipes: {type: Array, required: false, default: () => []}
})
const headers = [
    {title: 'Recipe', value: 'name'},
    {
        title: 'Ingredients', 
        key: 'ingredients',
        value: item => item.ingredients?.map(ing => ing.name).join(', ')
    },
    {title: 'Actions', key: 'actions', align: 'end', sortable: false}
]
const goToRecipe = async (id) => {
    await navigateTo({
        path: `/recipes/${id}`,
    })
}
</script>