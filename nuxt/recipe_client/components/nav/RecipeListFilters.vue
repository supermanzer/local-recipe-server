<template>
  <div>
    <IngredientSearch @ingredientSelected="setIngredients" />
    <v-spacer></v-spacer>
    <v-text-field
      v-model="options.search"
      label="Search by Name"
      append-icon="mdi-magnify"
    ></v-text-field>
  </div>
</template>

<script>
export default {
  data: () => ({
    options: {},
  }),
}
</script>
