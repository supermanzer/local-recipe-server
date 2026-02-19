<template>
    <v-card flat color="grey-lighten-3">
        <v-form class="my-6 px-4">
            <p class="text-h3 my-5">{{ name }}</p>
            <v-text-field
              v-model="formData.name"
              label="Recipe name"
              required
            />
            <!-- Ingredients -->
            <CreateIngredients
              v-model="formData.ingredients"
              :options="ingredientOptions"
              @update:model-value="formData.ingredients = $event"
            />
            <v-divider class="my-4"></v-divider>
            <!-- Steps -->
             <CreateSteps
             v-model="formData.steps"
             :ingredients="formData.ingredients"
             @update:model-value="formData.steps = $event"
             />
            <!-- Action Buttons -->
            <v-row class="action-buttons my-4" justify="space-around">
                <v-btn
                  color="secondary"
                  text="Cancel"
                  @click="$router.back()"
                />
                <v-btn
                  color="primary"
                  text="Save"
                  :loading="isSubmitting"
                  @click="submitRecipe"
                />
            </v-row>
        </v-form>
    </v-card>
</template>

<script setup lang="ts">
import type { RecipeCreatePayload, Ingredient } from '~/types/recipe.types';
import CreateIngredients from './CreateIngredients.vue';
import CreateSteps from './CreateSteps.vue';

const {createRecipe, updateRecipe, getRecipe, getIngredients, convertRecipeToFormData} = recipeUtils();

const route = useRoute()
const recipeId = route.params.id ? parseInt(route.params.id as string) : null;
const isEditMode = recipeId !== null;
const name = computed(() => isEditMode ? 'Edit Recipe' : 'New Recipe');
const ingredientOptions = ref<Ingredient[]>([]);

const isSubmitting = ref(false);

definePageMeta({
    name: name.value,
    middleware: ['auth']
});

const formData = ref<RecipeCreatePayload>({
    name: '',
    ingredients: [],
    steps: []
});


const submitRecipe = async() => {
    console.log("SUBMITTING RECIPE WITH DATA:\n", formData.alue);
    
    isSubmitting.value = true;
    let recipe = null;
    try {
        if (isEditMode && recipeId) {
           recipe = await updateRecipe(recipeId, formData.value);
        } else {
            recipe = await createRecipe(formData.value); 
        }
    } catch (error) {
        console.log(error);
    } finally {
        isSubmitting.value = false;
        if (recipe !== null) {
            await navigateTo(`/recipes/${recipe?.id}`);
        } else {
            await navigateTo('/');
        }
    }
}



onMounted( async() => {
    if (isEditMode && recipeId) {
        const recipe = await getRecipe(recipeId.toString());
        console.log("GOT RECIPE:\n", recipe);
        
        const formRecipe = convertRecipeToFormData(recipe)
        console.log("CONVERTED TO FORM DATA FORMAT:\n", formRecipe);
        
        formData.value.name = formRecipe.name;
        formData.value.ingredients = formRecipe.ingredients;

        formData.value.steps = formRecipe.steps;
    }
    ingredientOptions.value = await getIngredients();
})

</script>