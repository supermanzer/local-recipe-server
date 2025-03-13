<template>
  <v-row>
      <v-col cols="12" sm="12">
          <v-form v-if="hasRecipe">
              <v-list>
                  <v-subheader>Title</v-subheader>
                  <v-list-item>
                      <v-list-item-content>
                          <core-text-field
                            v-model="myRecipe.title"
                            ></core-text-field>
                      </v-list-item-content>
                  </v-list-item>
              </v-list>
            
            <v-list>
                <v-subheader>Ingredients</v-subheader>
                <v-list-item-group class="pa-2 mx-auto">
                    <v-list-item v-for="(ingredient, index) in myRecipe.ingredients" :key="index"
                    >
                        <RecipeIngredient
                            :ingredient="ingredient"
                            @input="updateIngredient(index, ingredient)" />   
                    </v-list-item>
                </v-list-item-group>
                <v-subheader>Steps</v-subheader>
                <v-list-item-group class="pa-2 mx-auto">
                    <v-list-item
                        v-for="(step, index) in myRecipe.steps"
                        :key="index"
                    >
                        <RecipeStep
                            :step="step"
                            @input="updateStep(index, step)" />
                    </v-list-item>
                </v-list-item-group>
            </v-list>
          </v-form>
          <v-row class="d-flex justify-space-around pa-4">
              <v-btn color="cancel" @click="resetForm">Reset</v-btn>
              <v-btn color="success" @click="confirmRecipe">Confirm Recipe</v-btn>
          </v-row>
      </v-col>
  </v-row>
</template>

<script>
export default {
    props: {
        recipe: {
            type: Object,
            default: () => {},
        },
    },
    emits: ['update:recipe'],
    data: () => ({
        myRecipe: null,
    }),
    computed: {
        hasRecipe() {
            return this.myRecipe !== null;
        },
    },
    mounted() {
        this.myRecipe = this.recipe;
    },
    methods: {
        updateRecipe() {
            this.$emit('update:recipe', this.myRecipe);
        },
        confirmRecipe() {
            this.$emit("confirm:recipe", this.myRecipe);
        },
        resetForm() {
            this.$emit("reset:recipe");
        },
        updateTitle(title) {
            this.myRecipe.title = title;
        },
        updateIngredient(index, ingredient) {
            this.myRecipe.ingredients[index] = ingredient;
        },
        updateStep(index, step) {
            this.myRecipe.steps[index] = step;
        },
    },
    
    
}
</script>
