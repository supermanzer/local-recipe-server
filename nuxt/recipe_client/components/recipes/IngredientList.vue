<template>
   <v-list :items="ingredients" item-title="name" item-value="id">
   
    <RecipesIngredientListItem  
      v-for="ingredient in ingredients" 
      :key="ingredient.id"  
      :ingredient="ingredient"
      :highlighted-ids="highlightedIds"
    />
   </v-list>
</template>

<script setup lang="js">
 const { ingredients, highlightedIds } = defineProps({
    ingredients: { type: Array, required: false, default: () => [] },
    highlightedIds: { type: Array, required: false, default: () => [] }
 })
</script>