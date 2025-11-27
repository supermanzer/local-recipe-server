/**
 * Provides utilities for interacting with the recipe REST API
 * @module recipeUtils
 */

import type { PaginatedRecipeResponse, Recipe } from "~/types/recipe.types";

export const recipeUtils = () => {
    const config = useRuntimeConfig();
    let baseURL = config.public.baseURL;
    console.log("BASE URL ", baseURL);
    if (!baseURL) {
        baseURL = "http://localhost:8585/api"

    }

    /**
     * Fetches all recipes from the API
     * @returns {Promise<Recipe[]>} A promise that resolves to an array of recipes
     */
    const getRecipes = async (): Promise<Recipe[]> => {

        const { results } = await $fetch<PaginatedRecipeResponse>('/recipes/', { baseURL: baseURL })
        console.log("Recipe Results: ", results);

        return results
    }
    const getRecipe = async (id: string): Promise<Recipe> => {
        return await $fetch<Recipe>(`/recipes/${id}`, {
            baseURL
        })
    }

    return {
        getRecipes,
        getRecipe
    }
}