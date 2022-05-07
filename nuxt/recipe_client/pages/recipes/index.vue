<template>
<div>
   <v-row>
       <v-col justify="center" align="center" class="my-6">
           <span class="text-h3">Your Local Recipes</span>
           <span class="mx-4">
               <v-btn
                class="mx-2"
                fab
                dark
                color="info"
                nuxt
                :to="{name: 'index'}"
               >
                <v-icon>mdi-home</v-icon>
               </v-btn>
           </span>
       </v-col>
   </v-row>
   <v-card>
       <v-card-title>
           <IngredientSearch @ingredientSelected="setIngredients"/>
           <v-spacer></v-spacer>
              <v-text-field
                v-model="options.search"
                label="Search by Name"
                append-icon="mdi-magnify"
                ></v-text-field>
       </v-card-title>
   </v-card>
   <v-data-table
       :headers="headers"
       :items="recipes"
       :options.sync="options"
       :server-items-length="totalRecipes"
       :search="search"
       :page.sync="options.page"
       hide-default-footer
       @click:row="viewRecipe"
   >
    <template v-slot:[`item.ingredients`]="{item}">
        <v-chip-group column>
            <v-chip
                v-for="ingredient in item.ingredients"
                :key="ingredient.name"
                color="primary"
            >
            {{ingredient.name}}
            </v-chip>
        </v-chip-group>
    </template>
   </v-data-table>
   <div class="text-center">
       <v-pagination
        v-model="options.page"
        :length="pageCount"
       ></v-pagination>
   </div>
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
           value: 'name',
       },{
            text: 'Ingredients',
            align: 'center',
            sortable: true,
            value: 'ingredients',
       }],
       recipes: [],
       options: {},
       search: '',
       ingredients: [],
       itemsPerPage: 10
   }),
   computed: {
       totalRecipes() {
           return this.recipes.length;
       },
       pageCount() {
           return Math.ceil(this.recipes.length/this.itemsPerPage)
       }
   },
   watch: {
       options: {
           handler() {
               this.filterRecipes();
           }
       }
   },
    methods: {
        setIngredients(e) {
            this.ingredients = e;
            this.filterRecipes();
        },
        async filterRecipes() {
            const requestOptions = {params:{}};
            
            if (this.options.search) {
                requestOptions.params.search = this.options.search;
            }
            if (this.ingredients.length > 0) {
                requestOptions.params.ingredients = this.ingredients;
            }
            /* eslint-disable no-console */
            const qs = this.$qs.stringify(requestOptions.params, {indices: false});
            const response = await this.$axios.$get(`/recipes/?${qs}`);
            this.recipes = response.results;
        },
        viewRecipe(item, related) {
            this.$router.push(`/recipes/${item.id}`)
        }
    }
}
</script>
