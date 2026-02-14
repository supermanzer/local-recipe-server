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


# New serializers for creation (NOT ModelSerializers - custom structure):
class IngredientInputSerializer(serializers.Serializer):
    """Input serializer for ingredient data during recipe creation"""

    name = serializers.CharField(max_length=200)
    amount = serializers.DecimalField(max_digits=5, decimal_places=2)
    unit = serializers.CharField(
        max_length=200, required=False, allow_blank=True
    )


class StepIngredientReferenceSerializer(serializers.Serializer):
    """References an ingredient by its index in the ingredients list"""

    ingredient_index = serializers.IntegerField(min_value=0)
    # ingredient_index maps to the ingredient at ingredients[index]


class StepInputSerializer(serializers.Serializer):
    """Input serializer for step data during recipe creation"""

    order = serializers.IntegerField(min_value=1)
    step = serializers.CharField()
    ingredients = StepIngredientReferenceSerializer(many=True, required=False)


class RecipeManageSerializer(serializers.Serializer):
    """
    Handles both recipe creation and updating with nested ingredients and steps.

    This is a regular Serializer (not ModelSerializer) because the structure
    doesn't directly map to a model. Both .create() and .update() methods
    orchestrate operations across multiple related models in atomic transactions.
    """

    id = serializers.IntegerField(
        required=False, read_only=True
    )  # Present only on update
    name = serializers.CharField(max_length=200)
    ingredients = IngredientInputSerializer(many=True)
    steps = StepInputSerializer(many=True)

    def create(self, validated_data):
        """
        Override .create() to handle recipe creation with nested objects.

        Process:
        1. Create Recipe instance with name
        2. For each ingredient:
           - Get or create Ingredient record
           - Create RecipeIngredient record (linking ingredient to recipe with amount/unit)
        3. For each step:
           - Create Step record (linked to recipe with order)
           - For each step ingredient reference:
             - Create StepIngredient record (linking step to recipe ingredient)

        All operations wrapped in transaction.atomic() for consistency.
        Returns the created Recipe instance.
        """

        pass

    def update(self, instance, validated_data):
        """
        Override .update() to handle recipe editing with nested objects.

        For updates, we preserve the Recipe ID but replace all related objects.
        This approach is simpler than trying to patch individual relationships.

        Process:
        1. Update Recipe.name if changed
        2. Delete all existing RecipeIngredients for this recipe
        3. Create new RecipeIngredients from validated_data
        4. Delete all existing Steps for this recipe
        5. Create new Steps and StepIngredients from validated_data

        All operations wrapped in transaction.atomic() for consistency.
        Returns the updated Recipe instance.
        """

        pass
