<template>
<div>
   <v-row>
       <v-col justify="center" align="center" class="my-6">
           <span class="text-h3">Your Local Recipes</span>
       </v-col>
   </v-row>
   <v-data-table
       :headers="headers"
       :items="recipes"
       class="elevation-2"
   ></v-data-table>
</div>
</template>
 
<script>
export default {
   name: 'RecipeHome',
   async asyncData({$http}) {
       const response = await $http.$get('/recipes');
       const recipes = response.results;
       return {
           recipes
       }
   },
   data: () => ({
       headers: [{
           text: 'Name',
           align: 'center',
           sortable: true,
           value: 'name'
       }],
       recipes: [],
   }),
  
}
</script>
