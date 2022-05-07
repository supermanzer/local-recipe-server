from rest_framework import serializers
from . import models
from logging import getLogger

logger = getLogger(__name__)


class RecipeIngredientSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        logger.info(
            'RecipeIngredientSerializer to_representation {}'.format(instance))
        return super().to_representation(instance)

    class Meta:
        model = models.RecipeIngredient
        fields = ''


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Image
        fields = ('id', 'image', 'recipe')


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = serializers.SerializerMethodField()

    class Meta:
        model = models.Recipe
        fields = ('id', 'name', 'ingredients', 'images', 'steps')

    def get_ingredients(self, obj):
        response = []
        for ingredient in obj.ingredients.all():
            recipe_ingredient = models.RecipeIngredient.objects.get(
                recipe=obj, ingredient=ingredient)
            amount = str(recipe_ingredient.amount)
            response.append(
                {"amount": amount, "unit": recipe_ingredient.unit, "name": ingredient.name})
        return response


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Ingredient
        fields = ('id', 'name')
