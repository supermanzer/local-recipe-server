<template>
    <v-card v-if="recipe !== null">
        <v-img
         :src="img"
         height="300"
         gradient="to top, rgba(0,0,0,0.8), rgba(0,0,0,0.2)"
         cover
         class="align-end text-white"
        >
            <v-card-title>{{ recipe.name }}</v-card-title>
        </v-img>
        <v-card-text>
            <v-row>
                <v-col cols="12" sm="12" md="4">
                    <RecipesIngredientList :ingredients="recipe.ingredients" />
                </v-col>
                <v-col cols="12" sm="12" md="8">
                    <RecipesStepList :steps="recipe.recipe_steps" />
                </v-col>
            </v-row>
            
            
        </v-card-text>
    </v-card>
</template>

<script setup lang="js">
const {getRecipe} = recipeUtils();
const route  = useRoute();
const {data:recipe, error} = useAsyncData('recipe', () => getRecipe(route.params.id))
const img = computed(() => {
    return (Object.hasOwn(recipe, 'img')) ? recipe.img : 'https://images.pexels.com/photos/952478/pexels-photo-952478.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2'
})
</script>