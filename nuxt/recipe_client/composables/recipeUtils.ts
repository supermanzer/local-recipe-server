/**
 * Provides utilities for interacting with the recipe REST API
 * @module recipeUtils
 */

import type { PaginatedRecipeResponse, Recipe } from "~/types/recipe.types";

export const recipeUtils = () => {
    const config = useRuntimeConfig();
    const baseURL = config.public.baseURL;


    /**
     * Fetches all recipes from the API
     * @returns {Promise<Recipe[]>} A promise that resolves to an array of recipes
     */
    const getRecipes = async (): Promise<Recipe[]> => {

        const { results } = await $fetch<PaginatedRecipeResponse>('/recipes/', { baseURL: baseURL })
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