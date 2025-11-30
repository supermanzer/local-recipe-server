/**
 * Provides utilities for interacting with the recipe REST API
 * @module recipeUtils
 */

import type { PaginatedIngredientResponse, Ingredient, PaginatedRecipeResponse, Recipe } from "~/types/recipe.types";

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

    const searchRecipes = async (ingredients: number[]): Promise<Recipe[]> => {
        console.log("Ingredients: ", ingredients);

        const params = new URLSearchParams()
        ingredients.forEach(id => {
            params.append('ingredients', id.toString())
        })

        const { results } = await $fetch<PaginatedRecipeResponse>(`/recipes/?${params.toString()}`, {
            baseURL: baseURL,
        })

        return results
    }

    const getIngredients = async (): Promise<Ingredient[]> => {
        const { results } = await $fetch<PaginatedIngredientResponse>('/ingredients/', {
            baseURL: baseURL
        });

        return results
    }

    return {
        getRecipes,
        getRecipe,
        searchRecipes,
        getIngredients
    }
}