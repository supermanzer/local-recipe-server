<template>
  <v-autocomplete
    v-model="selectedIngredients"
    chips
    multiple
    :items="ingredients"
    item-text="name"
    item-value="id"
    label="Filter by Ingredients"
    clearable
    @keyup="searchIngredients"
    @input="emitSelected"
  ></v-autocomplete>
</template>

<script>
export default {
    name: "IngedientSearch",
    data: () => ({
      selectedIngredients: [],
      ingredients: [],
    }),
    created() {
      this.fetchIngredients();
    },
    methods: {
      searchIngredients(e) {
          this.$http.$get('/ingredients/?search=' + e.target.value).then(response => {
            this.ingredients = response.results;
          });
      },
      async fetchIngredients() {
        const response = await this.$http.$get('/ingredients/');
        this.ingredients = response.results;
      },
      emitSelected() {
        this.$emit('ingredientSelected', this.selectedIngredients);
      }
    },
}
</script>
