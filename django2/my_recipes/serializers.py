from logging import getLogger

from rest_framework import serializers

from . import models

logger = getLogger(__name__)


class RecipeIngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.RecipeIngredient
        fields = ["id", "amount", "unit", "ingredient"]


class StepIngredientSerializer(serializers.ModelSerializer):
    ingredient = RecipeIngredientSerializer(read_only=True)

    class Meta:
        model = models.StepIngredient
        fields = ["id", "ingredient"]


class StepSerializer(serializers.ModelSerializer):
    step_ingredients = StepIngredientSerializer(
        source="stepingredient_set", many=True, read_only=True
    )

    class Meta:
        model = models.Step
        fields = ["id", "order", "step", "step_ingredients"]


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
