"""Backup and restore functionality for Recipe data models."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from django.db import transaction

from . import models


class RecipeBackup:
    """Handles backing up and restoring Recipe data with all related models."""

    @staticmethod
    def backup_recipe(recipe: models.Recipe) -> Dict[str, Any]:
        """
        Serialize a single recipe with all related data.

        Args:
            recipe: Recipe instance to backup

        Returns:
            Dictionary containing complete recipe data
        """
        ingredients = []
        for recipe_ingredient in recipe.recipeingredient_set.all():
            ingredients.append(
                {
                    "name": recipe_ingredient.ingredient.name,
                    "amount": str(recipe_ingredient.amount),
                    "unit": recipe_ingredient.unit,
                }
            )

        steps = []
        for step in recipe.recipe_steps.all().order_by("order"):
            step_ingredients = []
            for step_ingredient in step.stepingredient_set.all():
                step_ingredients.append(
                    {
                        "ingredient_name": step_ingredient.ingredient.ingredient.name,
                        "amount": str(step_ingredient.ingredient.amount),
                        "unit": step_ingredient.ingredient.unit,
                    }
                )

            steps.append(
                {
                    "order": step.order,
                    "step": step.step,
                    "ingredients": step_ingredients,
                }
            )

        return {
            "name": recipe.name,
            "steps_json": recipe.steps,
            "ingredients": ingredients,
            "steps": steps,
        }

    @staticmethod
    def backup_recipes(
        recipe_ids: Optional[List[int]] = None,
        output_file: Optional[str] = None,
        output_dir: Optional[str] = None,
    ) -> str:
        """
        Backup recipes to a JSON file.

        Args:
            recipe_ids: List of recipe IDs to backup. If None, backs up all recipes.
            output_file: Path to output JSON file. If None, creates timestamped file.
            output_dir: Path where JSON files should be saved

        Returns:
            Path to the created backup file
        """
        if recipe_ids:
            recipes = models.Recipe.objects.filter(id__in=recipe_ids)
        else:
            recipes = models.Recipe.objects.all()

        backup_data = {
            "timestamp": datetime.now().isoformat(),
            "count": recipes.count(),
            "recipes": [
                RecipeBackup.backup_recipe(recipe) for recipe in recipes
            ],
        }

        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            if output_dir is not None:
                output_file = f"{output_dir}/recipes_backup_{timestamp}.json"
            else:
                output_file = f"recipes_backup_{timestamp}.json"

        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w") as f:
            json.dump(backup_data, f, indent=2)

        return str(output_path)

    @staticmethod
    @transaction.atomic
    def restore_recipe(
        recipe_data: Dict[str, Any],
        overwrite: bool = False,
    ) -> models.Recipe:
        """
        Restore a single recipe from backup data.

        Args:
            recipe_data: Dictionary containing recipe data
            overwrite: If True, overwrite existing recipe with same name

        Returns:
            Created or updated Recipe instance
        """
        recipe_name = recipe_data["name"]

        # Check if recipe exists
        existing_recipe = models.Recipe.objects.filter(name=recipe_name).first()
        if existing_recipe:
            if not overwrite:
                # If we have this recipe already and we don't specify we should overwrite, skipp it
                return
            # Delete related records to start fresh
            existing_recipe.recipeingredient_set.all().delete()
            existing_recipe.recipe_steps.all().delete()
            recipe = existing_recipe
        else:
            recipe = models.Recipe(name=recipe_name)

        # Set steps JSON if provided
        if recipe_data.get("steps_json"):
            recipe.steps = recipe_data["steps_json"]

        recipe.save()

        # Create ingredients and recipe_ingredients
        ingredient_map = {}  # Map ingredient name to ID for step_ingredients

        for ingredient_data in recipe_data.get("ingredients", []):
            ingredient_name = ingredient_data["name"]
            # Get or create ingredient
            ingredient, _ = models.Ingredient.objects.get_or_create(
                name=ingredient_name
            )
            ingredient_map[ingredient_name] = ingredient

            # Create recipe ingredient relationship
            recipe_ingredient = models.RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient,
                amount=ingredient_data["amount"],
                unit=ingredient_data.get("unit"),
            )
            ingredient_map[f"{ingredient_name}_ri"] = recipe_ingredient

        # Create steps and step_ingredients
        for step_data in recipe_data.get("steps", []):
            step = models.Step.objects.create(
                recipe=recipe,
                order=step_data["order"],
                step=step_data["step"],
            )

            for step_ingredient_data in step_data.get("ingredients", []):
                ingredient_name = step_ingredient_data["ingredient_name"]

                # Get or create ingredient
                ingredient, _ = models.Ingredient.objects.get_or_create(
                    name=ingredient_name
                )

                # Get or create recipe ingredient
                recipe_ingredient, _ = (
                    models.RecipeIngredient.objects.get_or_create(
                        recipe=recipe,
                        ingredient=ingredient,
                        defaults={
                            "amount": step_ingredient_data["amount"],
                            "unit": step_ingredient_data.get("unit"),
                        },
                    )
                )

                # Create step ingredient relationship
                models.StepIngredient.objects.create(
                    step=step,
                    ingredient=recipe_ingredient,
                )

        return recipe

    @staticmethod
    @transaction.atomic
    def restore_recipes(
        input_file: str,
        overwrite: bool = False,
    ) -> List[models.Recipe]:
        """
        Restore recipes from a JSON backup file.

        Args:
            input_file: Path to JSON backup file
            overwrite: If True, overwrite existing recipes with same names

        Returns:
            List of created/updated Recipe instances
        """
        with open(input_file, "r") as f:
            backup_data = json.load(f)

        restored_recipes = []
        for recipe_data in backup_data.get("recipes", []):
            recipe = RecipeBackup.restore_recipe(
                recipe_data, overwrite=overwrite
            )
            restored_recipes.append(recipe)

        return restored_recipes
