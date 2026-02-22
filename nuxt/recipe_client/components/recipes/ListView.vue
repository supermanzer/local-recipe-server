<template>
    <v-data-table
    v-if="recipes !== null"
    :headers="headers"
     :items="recipes"
    >
        <template v-slot:header.ingredients="{column}">
            {{ selectedIngredientNames.length === 0 ? column.title : "Remaining Ingredients" }}
        </template>
        <template #item="{item}">
            <list-view-item :item="item" :selected-ingredients="selectedIngredientNames" />  
        </template>
    </v-data-table>
    <div v-else>
        <p class="text-h1">RECIPES GO HERE</p>
    </div>
</template>

<script setup lang="js">
import ListViewItem from './ListViewItem.vue';


const {recipes} = defineProps({
    recipes: {type: Array, required: false, default: () => []},
    selectedIngredientNames: {type: Array, required: false, default: () => []}
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
</script>