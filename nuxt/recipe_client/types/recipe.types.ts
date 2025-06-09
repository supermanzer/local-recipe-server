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
    title: string;
    /** Full description of the recipe */
    description: string;
    // Add other recipe-specific fields here
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