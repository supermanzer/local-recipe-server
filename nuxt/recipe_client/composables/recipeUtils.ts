/**
 * Provides utilities for interacting with the recipe REST API
 * @module recipeUtils
 */

import type { PaginatedIngredientResponse, Ingredient, PaginatedRecipeResponse, Recipe, ActionResponse } from "~/types/recipe.types";

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

    return {
        getRecipes,
        getRecipe,
        searchRecipes,
        getIngredients,
        triggerBackup,
        triggerRestore,
        downloadLatestBackup
    }
}