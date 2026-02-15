/**
 * Provides utilities for interacting with the recipe REST API
 * @module recipeUtils
 */

import type { PaginatedIngredientResponse, Ingredient, PaginatedRecipeResponse, Recipe, ActionResponse, RecipeCreatePayload } from "~/types/recipe.types";

export const recipeUtils = () => {
    const { makeAuthRequest } = useAuth();
    const config = useRuntimeConfig();
    let baseURL = config.public.baseURL;
    if (!baseURL) {
        baseURL = "http://localhost:8585/api"
    }
    /**
     * Fetches all recipes from the API
     * @returns {Promise<Recipe[]>} A promise that resolves to an array of recipes
     */
    const getRecipes = async (): Promise<Recipe[]> => {
        console.log("GETTING RECIPES");

        const response = await makeAuthRequest<PaginatedRecipeResponse>('/recipes/', "GET")
        console.log("RECIPE UTILS /recipes/ response:  ", response);
        return response.results
    }
    const getRecipe = async (id: string): Promise<Recipe> => {

        const url = `/recipes/${id}`
        const response = await makeAuthRequest<Promise<Recipe>>(url, "GET");
        return response
    }

    const searchRecipes = async (ingredients: number[]): Promise<Recipe[]> => {
        console.log("Ingredients: ", ingredients);

        const params = new URLSearchParams()
        ingredients.forEach(id => {
            params.append('ingredients', id.toString())
        })
        const url = `/recipes/?${params.toString()}`
        const { results } = await makeAuthRequest<PaginatedRecipeResponse>(url, "GET")
        return results
    }

    const getIngredients = async (): Promise<Ingredient[]> => {
        const url = '/ingredients/'
        const { results } = await makeAuthRequest<PaginatedIngredientResponse>(url, "GET")
        return results
    }

    const triggerBackup = async (): Promise<ActionResponse> => {
        const url = '/recipes/backup_recipes/'
        const result = await makeAuthRequest<Promise<ActionResponse>>(url, "POST")
        return result
    }

    const triggerRestore = async (file: File, overwrite: boolean): Promise<ActionResponse> => {
        const formData = new FormData();

        formData.append("backup_file", file);
        formData.append('overwrite', overwrite.toString());

        const url = '/recipes/restore_recipes/'

        const result = await makeAuthRequest<ActionResponse>(
            url,
            "POST",
            formData
        )

        return result
    }

    const downloadLatestBackup = async () => {
        const link = document.createElement('a');
        link.href = `${baseURL}/recipes/download_backup/`;
        link.download = '';  // Browser will use Content-Disposition filename
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        // Browser will automatically download the file
    }

    /**
     * Converts a Recipe API response to RecipeCreatePayload format for form editing.
     *
     * Transforms the nested API structure (RecipeIngredient with nested Ingredient)
     * to the flat form structure expected by the create/edit form.
     *
     * @param recipe - Recipe object from API (includes recipe_steps and nested ingredients)
     * @returns RecipeCreatePayload - Formatted data ready for form display/submission
     */
    const convertRecipeToFormData = (recipe: Recipe): RecipeCreatePayload => {
        return {
            name: recipe.name,
            // Flatten ingredients: transform from RecipeIngredient to RecipeIngredientInput
            ingredients: recipe.ingredients.map(recipeIngredient => ({
                name: recipeIngredient.ingredient.name,
                amount: Number(recipeIngredient.amount),
                unit: recipeIngredient.unit || ''
            })),
            // Map steps and resolve ingredient indices
            steps: recipe.recipe_steps.map(step => ({
                order: step.order,
                step: step.step,
                // For each ingredient used in this step, find its index in the flattened ingredients array
                ingredients: step.step_ingredients.map(stepIngredient => ({
                    ingredient_index: recipe.ingredients.findIndex(
                        recipeIngredient =>
                            recipeIngredient.ingredient.id === stepIngredient.ingredient.id
                    )
                }))
            }))
        }
    }

    const createRecipe = async (recipeData: RecipeCreatePayload): Promise<Recipe> => {
        const url = '/recipes/'
        const response = await makeAuthRequest<Recipe>(url, "POST", recipeData)
        return response
    }

    const updateRecipe = async (recipeId: number, recipeData: RecipeCreatePayload): Promise<Recipe> => {
        console.log("GOT UPDATE REQUEST FOR RECIPE ", recipeId);
        console.log("RECIPE DATA:\n", recipeData);
        const url = `/recipes/${recipeId}/`
        const response = await makeAuthRequest<Recipe>(url, "PUT", recipeData)
        return response
    }

    return {
        getRecipes,
        getRecipe,
        searchRecipes,
        getIngredients,
        triggerBackup,
        triggerRestore,
        downloadLatestBackup,
        convertRecipeToFormData,
        createRecipe,
        updateRecipe,
    }
}