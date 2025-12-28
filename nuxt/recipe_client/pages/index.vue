<template>
    <div>
        <p class="text-h1">Recipes</p>
        <recipes-search-bar @ingedient-selected="filterRecipes" />
        <recipes-list-view v-if="recipes" :recipes="recipes" />
    </div>
</template>

<script setup lang="ts">
import type { Recipe } from '~/types/recipe.types';

definePageMeta({
    name: "RecipesHome",
    middleware: 'auth'
});


const {getRecipes, searchRecipes} = recipeUtils();

const recipes = ref<Recipe[]>([]);

const {data, error} = await useAsyncData('recipes',() => getRecipes());

if (data.value) {
    recipes.value = data.value;
} else {
    console.log("GOT ERROR: ", error)
}

const filterRecipes = async (ids: number[]) => {
    console.log("Filtering recipes!");
    
    const filtered = await searchRecipes(ids);
    recipes.value = filtered;
    console.log("Recipes filtered to: ", filtered);
    
}
</script>