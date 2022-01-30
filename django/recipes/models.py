from operator import mod
from pyexpat import model
from unicodedata import name
from django.db import models


def recipe_image_file_path(instance, filename):
    return 'recipe_{0}/{1}'.format(instance.id, filename)


class Recipe(models.Model):
    """Highest leve model representing a recipe"""
    name = models.CharField(max_length=200)
    ingredients = models.ManyToManyField(
        'Ingredient', through='RecipeIngredient')
    # Might try this approach simultaneously with the Step model approach
    steps = models.JSONField(default=dict)

    class Meta:
        ordering = ('name',)

    def __str__(self) -> str:
        return self.name


class Image(models.Model):
    """An image associated with a recipe"""
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    image = models.FileField(upload_to=recipe_image_file_path)


class Step(models.Model):
    """An individual step in a recipe"""
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    order = models.PositiveIntegerField()
    step = models.TextField()


class Ingredient(models.Model):
    """An individual ingredient."""
    name = models.CharField(max_length=200)


class RecipeIngredient(models.Model):
    """A relationship between a recipe and an ingredient."""
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=5, decimal_places=2)
    unit = models.CharField(max_length=200)
