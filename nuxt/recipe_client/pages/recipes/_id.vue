<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12" sm="12">
        <h1 class="h3 my-4">{{ recipe.name }}</h1>
        <v-divider></v-divider>
      </v-col>
      <v-col cols="12" sm="12" md="4" lg="3">
        <v-card class="d-block word-wrap">
          <v-card-title> Ingredients </v-card-title>
          <v-divider></v-divider>
          <v-list subheader>
            <v-list-item-group>
              <Display
                v-for="ingredient in recipe.ingredients"
                :key="ingredient.id"
                :ingredient="ingredient"
              ></Display>
            </v-list-item-group>
          </v-list>
        </v-card>
      </v-col>
      <v-col cols="12" sm="12" md="8" lg="9">
        <RecipeDisplayStep
          v-for="step in recipe.recipe_steps"
          :key="step.id"
          :step="step"
        />
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import Display from '~/components/ingredient/display.vue'
export default {
  name: 'RecipeDetail',
  components: { Display },
  layout: 'recipe',
  async asyncData({ $http, params }) {
    const recipe = await $http.$get(`/recipes/${params.id}/`)
    return { recipe }
  },
  data: () => ({}),
}
</script>

<style lang="css">
.word-wrap {
  overflow-wrap: break-word;
}
</style>
