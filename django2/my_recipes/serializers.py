from logging import getLogger

from rest_framework import serializers

from . import models

logger = getLogger(__name__)


class StepSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Step
        fields = ["id", "order", "step"]


class RecipeIngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.RecipeIngredient


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = serializers.SerializerMethodField()
    recipe_steps = StepSerializer(many=True, read_only=True)

    def get_ingredients(self, obj: models.Recipe):
        return [
            {
                "id": ri.id,
                "amount": str(ri.amount),
                "unit": ri.unit,
                "name": ingredient.name,
            }
            for ingredient in obj.ingredients.all().distinct()
            for ri in models.RecipeIngredient.objects.filter(
                recipe=obj, ingredient=ingredient
            )
        ]

    class Meta:
        model = models.Recipe
        fields = ("id", "name", "ingredients", "recipe_steps")


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Ingredient
        fields = ("id", "name")
