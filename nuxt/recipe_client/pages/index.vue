<template>
    <p class="text-h1">Recipes</p>
    <recipes-list-view :recipes="recipes" />
</template>

<script setup lang="js">
definePageMeta({
    name: "RecipesHome"
});

const {getRecipes} = recipeUtils();
onMounted(async () => {
    const {data: recipes, error} = await useAsyncData('recipes',() => getRecipes());
})

console.log(recipes);



</script>