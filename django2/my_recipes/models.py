from django.db import models


# Create your models here.
class Recipe(models.Model):
    """Highest level model representing a recipe"""

    created_at = models.DateTimeField(
        verbose_name="Recipe Created",
        auto_now_add=True,
    )
    modified_at = models.DateTimeField(
        auto_now=True, verbose_name="Recipe modified"
    )
    name = models.CharField(max_length=200)
    ingredients = models.ManyToManyField(
        "Ingredient", through="RecipeIngredient"
    )
    # Might try this approach simultaneously with the Step model approach
    steps = models.JSONField(default=dict, null=True, blank=True)

    class Meta:
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name

    def recipe_ingredients(self):
        return ", ".join(
            ingredient.name for ingredient in self.ingredients.all()[:5]
        )


class Step(models.Model):
    """An individual step in a recipe"""

    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name="recipe_steps"
    )
    order = models.PositiveIntegerField()
    step = models.TextField()
    # TODO: Add M2M relationship with Ingredient model - this will allow for highlighting which ingredients in the Recipe Ingredient relationship pertain to this step

    def __str__(self) -> str:
        return f"{self.order} - {self.step}"


class Ingredient(models.Model):
    """An individual ingredient."""

    name = models.CharField(max_length=200, unique=True)

    class Meta:
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return self.name


class RecipeIngredient(models.Model):
    """A relationship between a recipe and an ingredient."""

    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=5, decimal_places=2)
    unit = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.recipe}: {self.ingredient} - {self.amount} {self.unit}"


class StepIngredient(models.Model):
    """A relationship entity between a Recipe Step and Ingredient.

    This provides the relationship to allow highlighting in the UI when a specific step is being worked on.
    """

    step = models.ForeignKey(Step, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(RecipeIngredient, on_delete=models.CASCADE)
