from rest_framework import serializers
from . import models
from logging import getLogger

logger = getLogger(__name__)

class StepSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Step
        fields = ['id', 'order', 'step']


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
    recipe_steps = StepSerializer(
        many=True, read_only=True
    )

    class Meta:
        model = models.Recipe
        fields = ('id', 'name', 'ingredients', 'images', 'recipe_steps')

    def get_ingredients(self, obj):
        response = []
        for ingredient in obj.ingredients.all().distinct():
            recipe_ingredients = models.RecipeIngredient.objects.filter(
                recipe=obj, ingredient=ingredient)
            for ri in recipe_ingredients:
                amount = str(ri.amount)
                response.append(
                    {"id": ri.id,"amount": amount, "unit": ri.unit, "name": ingredient.name})
        return response


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Ingredient
        fields = ('id', 'name')
