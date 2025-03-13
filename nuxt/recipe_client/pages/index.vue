<template>
 <v-row justify="center" align="center">
   <v-col cols="12" sm="8" md="6">
    <v-card>
      <v-card-title>
        Local Recipes
      </v-card-title>
     <v-card-actions>
       <v-btn color="primary" @click="$router.push('/recipes')">View Recipes</v-btn>
       <v-spacer></v-spacer>
       <v-btn color="primary" @click="$router.push('/recipes/create')">Create Recipe</v-btn>
     </v-card-actions>
    </v-card>
   </v-col>
 </v-row>
</template>
 
<script>
export default {
 name: 'Landing',
 data: () => ({
   routes: [
     {
       path: '/',
       name: 'Home',
 
     },
     {
       path: '/recipes',
       name: 'Recipes',
     
     },
     {
       path: '/recipes/create',
       name: 'CreateRecipe',
  
     },
    
   ]
 })
}
</script>