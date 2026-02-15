/**
 * Type definitions for the Recipe API responses
 * @packageDocumentation
 */


/**
 * Represents a recipe entity from the API
 * @interface Recipe
 */
export interface Recipe {
    /** Unique identifier for the recipe */
    id: number;
    /** Name of the recipe */
    name: string;
    /** Full description of the recipe */
    description: string;
    // Add other recipe-specific fields here
    ingredients: RecipeIngredient[];
    recipe_steps: RecipeStep[];
}

export interface RecipeStep {
    id?: number;
    order: number;
    step: string;
    ingredients: RecipeIngredient[];
}

/**
 * Represents a paginated response containing recipe data
 * @interface PaginatedRecipeResponse
 */
export interface PaginatedRecipeResponse {
    /** Total number of recipes available */
    count: number;
    /** URL for the next page of results, null if no next page exists */
    next: string | null;
    /** URL for the previous page of results, null if no previous page exists */
    previous: string | null;
    /** Array of recipe objects for the current page */
    results: Recipe[];
}

export interface Ingredient {
    // The ID of the Ingredient record
    id: number;
    // The name of the igredient
    name: string;
}

export interface RecipeIngredient {
    id?: number;
    name: string;
    amount: number | string;
    unit: string;
}

export interface PaginatedIngredientResponse {
    count: number;
    next: string | null;
    previous: string | null;
    results: Ingredient[];
}

export interface ActionResponse {
    status: string | null;
    message: string | null;
    error: string | null;
}

/**
 * Types for Recipe Create & Update actions
 */

export interface RecipeIngredientInput {
    name: string;
    amount: number | string;
    unit: string;
}

export interface StepIngredientReference {
    ingredient_index: number;
}

export interface RecipeStepInput {
    order: number;
    step: string;
    ingredients: StepIngredientReference[];
}

export interface RecipeCreatePayload {
    name: string;
    ingredients: RecipeIngredientInput[];
    steps: RecipeStepInput[];
}