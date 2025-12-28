/**
 * Provides utilities for interacting with the recipe REST API
 * @module recipeUtils
 */

import type { PaginatedIngredientResponse, Ingredient, PaginatedRecipeResponse, Recipe, ActionResponse } from "~/types/recipe.types";

export const recipeUtils = () => {
    const config = useRuntimeConfig();
    let baseURL = config.public.baseURL;
    const { accessToken } = useAuth();

    const authHeader = { Authorization: `Bearer ${accessToken.value}` }

    console.log("BASE URL ", baseURL);
    if (!baseURL) {
        baseURL = "http://localhost:8585/api"

    }

    /**
     * Fetches all recipes from the API
     * @returns {Promise<Recipe[]>} A promise that resolves to an array of recipes
     */
    const getRecipes = async (): Promise<Recipe[]> => {

        const { results } = await $fetch<PaginatedRecipeResponse>('/recipes/', {
            baseURL,
            method: 'GET',
            headers: authHeader
        })
        console.log("RECIPE COUNT: ", results.length);

        return results
    }
    const getRecipe = async (id: string): Promise<Recipe> => {
        return await $fetch<Recipe>(`/recipes/${id}`, {
            baseURL,
            method: 'GET',
            headers: authHeader
        })
    }

    const searchRecipes = async (ingredients: number[]): Promise<Recipe[]> => {
        console.log("Ingredients: ", ingredients);

        const params = new URLSearchParams()
        ingredients.forEach(id => {
            params.append('ingredients', id.toString())
        })

        const { results } = await $fetch<PaginatedRecipeResponse>(`/recipes/?${params.toString()}`, {
            baseURL: baseURL,
            method: 'GET',
            headers: authHeader
        })

        return results
    }

    const getIngredients = async (): Promise<Ingredient[]> => {
        const { results } = await $fetch<PaginatedIngredientResponse>('/ingredients/', {
            baseURL,
            method: 'GET',
            headers: authHeader
        });

        return results
    }

    const triggerBackup = async (): Promise<ActionResponse> => {
        const result = await $fetch<ActionResponse>('/recipes/backup_recipes/', {
            baseURL: baseURL,
            method: "POST",
            headers: authHeader
        })
        return result
    }

    const triggerRestore = async (file: File, overwrite: boolean): Promise<ActionResponse> => {
        const formData = new FormData();

        formData.append("backup_file", file);
        formData.append('overwrite', overwrite.toString());

        const result = await $fetch<ActionResponse>('/recipes/restore_recipes/', {
            baseURL: baseURL,
            method: 'POST',
            body: formData,
            headers: authHeader
        });

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