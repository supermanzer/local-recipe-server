"""
    services/orchestration.py
    
    Coordinate the various services to respond to a create recipe request.
"""

from logging import getLogger
from .image_ocr import load_images_return_text
from .text_assignment import assign_text_to_recipe

from recipes.models import Recipe, RecipeIngredient, Ingredient

logger = getLogger(__name__)


def create_recipe_json(image_paths: list) -> dict:
    """
        Orchestrate the various services to respond to a create recipe request.
    """
    logger.info('Creating recipe json from image paths: {}'.format(image_paths))

    full_text = load_images_return_text(image_paths)
    recipe_json = assign_text_to_recipe(full_text)

    return recipe_json


def create_recipe_records(recipe_json: dict) -> dict:
    """
        Orchestrate the creation of database records to form a recipe.
    """
    logger.info(
        'Creating recipe records from recipe json: {}'.format(recipe_json))

    # recipe_id = 12
    recipe = Recipe.objects.create(
        name=recipe_json['title'],
        steps=recipe_json['steps'],
    )
    for ingredient in recipe_json["ingredients"]:
        ingredient_record, _ = Ingredient.objects.get_or_create(
            name=ingredient['name'],
        )
        ri = RecipeIngredient(
            recipe=recipe,
            ingredient=ingredient_record,
            amount=ingredient['quantity'],
            unit=ingredient['unit'],
        )
        ri.save()

    return recipe.id
