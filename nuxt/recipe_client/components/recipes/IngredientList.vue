<template>
   <v-list :items="ingredients" item-title="name" item-value="id">
   
    <RecipesIngredientListItem  
      v-for="ingredient in ingredients" 
      :key="ingredient.id"  
      :ingredient="ingredient"
    />
   </v-list>
</template>

<script setup lang="js">
 const { ingredients } = defineProps({
    ingredients: {type: Array, required: false, default: () => []}
 })
</script>