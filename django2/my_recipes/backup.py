"""Backup and restore functionality for Recipe data models."""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from django.db import transaction

from . import models

logger = logging.getLogger(__name__)


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
        logger.info(f"Backing up recipe: {recipe.name} (ID: {recipe.id})")

        ingredients = []
        for recipe_ingredient in recipe.recipeingredient_set.all():
            logger.debug(
                f"  - Ingredient: {recipe_ingredient.ingredient.name} "
                f"({recipe_ingredient.amount} {recipe_ingredient.unit})"
            )
            ingredients.append(
                {
                    "name": recipe_ingredient.ingredient.name,
                    "amount": str(recipe_ingredient.amount),
                    "unit": recipe_ingredient.unit,
                }
            )

        logger.debug(
            f"Recipe '{recipe.name}' has {len(ingredients)} ingredients"
        )

        steps = []
        for step in recipe.recipe_steps.all().order_by("order"):
            logger.debug(f"  - Step {step.order}: {step.step[:50]}...")
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

        logger.debug(f"Recipe '{recipe.name}' has {len(steps)} steps")

        backup_data = {
            "name": recipe.name,
            "steps_json": recipe.steps,
            "ingredients": ingredients,
            "steps": steps,
        }

        logger.info(f"Successfully serialized recipe: {recipe.name}")
        return backup_data

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
        logger.info("Starting backup process...")
        if recipe_ids:
            logger.info(f"Backing up specific recipe IDs: {recipe_ids}")
            recipes = models.Recipe.objects.filter(id__in=recipe_ids)
        else:
            logger.info("Backing up all recipes")
            recipes = models.Recipe.objects.all()

        recipe_count = recipes.count()
        logger.info(f"Found {recipe_count} recipes to backup")

        backup_data = {
            "timestamp": datetime.now().isoformat(),
            "count": recipe_count,
            "recipes": [
                RecipeBackup.backup_recipe(recipe) for recipe in recipes
            ],
        }

        logger.debug(
            f"Backup data prepared: {len(backup_data['recipes'])} recipes serialized"
        )

        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            if output_dir is not None:
                output_file = f"{output_dir}/recipes_backup_{timestamp}.json"
                logger.debug(f"Using output directory: {output_dir}")
            else:
                output_file = f"recipes_backup_{timestamp}.json"
            logger.debug(f"Generated timestamped filename: {output_file}")

        output_path = Path(output_file)
        logger.debug(
            f"Creating output directories if needed: {output_path.parent}"
        )
        output_path.parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"Writing backup to file: {output_path}")
        with open(output_path, "w") as f:
            json.dump(backup_data, f, indent=2)

        logger.info(f"Backup completed successfully: {output_path}")
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
        logger.info(f"Restoring recipe: {recipe_name}")

        # Check if recipe exists
        existing_recipe = models.Recipe.objects.filter(name=recipe_name).first()
        if existing_recipe:
            if not overwrite:
                logger.warning(
                    f"Recipe '{recipe_name}' already exists and overwrite=False. Skipping."
                )
                # If we have this recipe already and we don't specify we should overwrite, skip it
                return
            logger.info(
                f"Recipe '{recipe_name}' exists. Overwriting existing recipe."
            )
            # Delete related records to start fresh
            logger.debug(f"Deleting existing ingredients for '{recipe_name}'")
            existing_recipe.recipeingredient_set.all().delete()
            logger.debug(f"Deleting existing steps for '{recipe_name}'")
            existing_recipe.recipe_steps.all().delete()
            recipe = existing_recipe
        else:
            logger.debug(f"Creating new recipe: {recipe_name}")
            recipe = models.Recipe(name=recipe_name)

        # Set steps JSON if provided
        if recipe_data.get("steps_json"):
            logger.debug(f"Setting steps JSON for '{recipe_name}'")
            recipe.steps = recipe_data["steps_json"]

        recipe.save()
        logger.debug(f"Saved recipe to database: {recipe_name}")

        # Create ingredients and recipe_ingredients
        ingredient_map = {}  # Map ingredient name to ID for step_ingredients

        ingredients_count = len(recipe_data.get("ingredients", []))
        logger.info(
            f"Creating {ingredients_count} recipe ingredients for '{recipe_name}'"
        )

        for ingredient_data in recipe_data.get("ingredients", []):
            ingredient_name = ingredient_data["name"]
            logger.debug(
                f"  Creating recipe ingredient: {ingredient_name} "
                f"({ingredient_data['amount']} {ingredient_data.get('unit', '')})"
            )
            # Get or create ingredient
            ingredient, created = models.Ingredient.objects.get_or_create(
                name=ingredient_name
            )
            if created:
                logger.debug(f"    Created new ingredient: {ingredient_name}")
            else:
                logger.debug(
                    f"    Using existing ingredient: {ingredient_name}"
                )
            ingredient_map[ingredient_name] = ingredient

            # Create recipe ingredient relationship
            recipe_ingredient = models.RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient,
                amount=ingredient_data["amount"],
                unit=ingredient_data.get("unit"),
            )
            logger.debug("    Created recipe ingredient record")
            ingredient_map[f"{ingredient_name}_ri"] = recipe_ingredient

        # Create steps and step_ingredients
        steps_count = len(recipe_data.get("steps", []))
        logger.info(f"Creating {steps_count} recipe steps for '{recipe_name}'")

        for step_data in recipe_data.get("steps", []):
            logger.debug(
                f"  Creating step {step_data['order']}: {step_data['step'][:50]}..."
            )
            step = models.Step.objects.create(
                recipe=recipe,
                order=step_data["order"],
                step=step_data["step"],
            )
            logger.debug(f"    Step {step_data['order']} created in database")

            for step_ingredient_data in step_data.get("ingredients", []):
                ingredient_name = step_ingredient_data["ingredient_name"]
                logger.debug(
                    f"    Linking ingredient '{ingredient_name}' to step {step_data['order']}"
                )

                # Get or create ingredient
                ingredient, created = models.Ingredient.objects.get_or_create(
                    name=ingredient_name
                )
                if created:
                    logger.debug(
                        f"      Created new ingredient: {ingredient_name}"
                    )

                # Get or create recipe ingredient
                recipe_ingredient, created = (
                    models.RecipeIngredient.objects.get_or_create(
                        recipe=recipe,
                        ingredient=ingredient,
                        defaults={
                            "amount": step_ingredient_data["amount"],
                            "unit": step_ingredient_data.get("unit"),
                        },
                    )
                )
                if created:
                    logger.debug("      Created new recipe ingredient record")

                # Create step ingredient relationship
                models.StepIngredient.objects.create(
                    step=step,
                    ingredient=recipe_ingredient,
                )
                logger.debug("      Step ingredient relationship created")

        logger.info(f"Successfully restored recipe: {recipe_name}")
        return recipe

    @staticmethod
    @transaction.atomic
    def restore_recipes(
        input_file,
        overwrite: bool = False,
    ) -> List[models.Recipe]:
        """
        Restore recipes from a JSON backup file or file object.

        Args:
            input_file: Either a file path (str) or an uploaded file object
            overwrite: If True, overwrite existing recipes with same names

        Returns:
            List of created/updated Recipe instances
        """
        logger.info("Starting restore process...")

        # Handle both file paths and uploaded file objects
        if hasattr(input_file, "read"):
            # It's a file object (InMemoryUploadedFile, etc.)
            logger.debug("Input is a file object (uploaded file)")
            content = input_file.read()
            if isinstance(content, bytes):
                logger.debug("Decoding bytes content to UTF-8")
                content = content.decode("utf-8")
            backup_data = json.loads(content)
            logger.debug("Parsed JSON from uploaded file")
        else:
            # It's a file path
            logger.debug(f"Input is a file path: {input_file}")
            with open(input_file, "r") as f:
                backup_data = json.load(f)
            logger.debug("Loaded backup data from file")

        backup_timestamp = backup_data.get("timestamp", "unknown")
        recipe_count = backup_data.get("count", 0)
        logger.info(
            f"Backup metadata - Timestamp: {backup_timestamp}, "
            f"Recipes to restore: {recipe_count}, Overwrite: {overwrite}"
        )

        restored_recipes = []
        for idx, recipe_data in enumerate(backup_data.get("recipes", []), 1):
            logger.info(f"Processing recipe {idx}/{recipe_count}")
            try:
                recipe = RecipeBackup.restore_recipe(
                    recipe_data, overwrite=overwrite
                )
                if recipe:
                    restored_recipes.append(recipe)
            except Exception as e:
                logger.error(
                    f"Failed to restore recipe {idx}: {recipe_data.get('name', 'unknown')}. "
                    f"Error: {str(e)}"
                )
                raise

        logger.info(
            f"Restore completed successfully. "
            f"Restored {len(restored_recipes)} recipes out of {recipe_count}"
        )
        return restored_recipes
