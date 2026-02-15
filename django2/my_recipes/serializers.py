from logging import getLogger

from django.db import transaction
from rest_framework import serializers

from my_recipes.models import (
    Ingredient,
    Recipe,
    RecipeIngredient,
    Step,
    StepIngredient,
)

logger = getLogger(__name__)


class RecipeIngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipeIngredient
        fields = ["id", "amount", "unit", "ingredient"]


class StepIngredientSerializer(serializers.ModelSerializer):
    ingredient = RecipeIngredientSerializer(read_only=True)

    class Meta:
        model = StepIngredient
        fields = ["id", "ingredient"]


class StepSerializer(serializers.ModelSerializer):
    step_ingredients = StepIngredientSerializer(
        source="stepingredient_set", many=True, read_only=True
    )

    class Meta:
        model = Step
        fields = ["id", "order", "step", "step_ingredients"]


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = serializers.SerializerMethodField()
    recipe_steps = StepSerializer(many=True, read_only=True)

    def get_ingredients(self, obj: Recipe):
        return [
            {
                "id": ri.id,
                "amount": str(ri.amount),
                "unit": ri.unit,
                "name": ingredient.name,
            }
            for ingredient in obj.ingredients.all().distinct()
            for ri in RecipeIngredient.objects.filter(
                recipe=obj, ingredient=ingredient
            )
        ]

    class Meta:
        model = Recipe
        fields = ("id", "name", "ingredients", "recipe_steps")


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
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
        Detailed implementation of atomic recipe creation.

        Key considerations:
        - Ingredient reuse: get_or_create() handles existing ingredients
        - Amount/unit tracking: stored on RecipeIngredient, not Ingredient
        - Step ordering: provided by frontend
        - Step-ingredient linking: uses ingredient_index to reference items
        """

        with transaction.atomic():
            # 1. Create recipe
            recipe = Recipe.objects.create(name=validated_data["name"])

            # 2. Create/link ingredients
            ingredient_map = {}  # Maps ingredient_index → RecipeIngredient ID

            for ingredient_data in validated_data["ingredients"]:
                # Get or create the base ingredient
                ingredient, _ = Ingredient.objects.get_or_create(
                    name=ingredient_data["name"]
                )

                # Create recipe ingredient link with amount/unit
                recipe_ingredient = RecipeIngredient.objects.create(
                    recipe=recipe,
                    ingredient=ingredient,
                    amount=ingredient_data["amount"],
                    unit=ingredient_data.get("unit", ""),
                )

                # Store for step ingredient references
                ingredient_map[len(ingredient_map)] = recipe_ingredient

            # 3. Create steps and step-ingredient links
            for step_data in validated_data["steps"]:
                step = Step.objects.create(
                    recipe=recipe,
                    order=step_data["order"],
                    step=step_data["step"],
                )

                # 4. Link ingredients to this step
                for step_ingredient_ref in step_data.get("ingredients", []):
                    ingredient_index = step_ingredient_ref["ingredient_index"]
                    recipe_ingredient = ingredient_map[ingredient_index]

                    StepIngredient.objects.create(
                        step=step, ingredient=recipe_ingredient
                    )

            return recipe

    def update(self, instance, validated_data):
        """
        Detailed implementation of atomic recipe updates.

        Strategy: Replace all related objects (RecipeIngredients and Steps).
        This is simpler than patching individual relationships and ensures
        consistency - we know exactly what ingredients and steps exist after update.

        Key considerations:
        - Preserve Recipe ID (the instance parameter)
        - Update Recipe.name if changed
        - Delete all old RecipeIngredients (cascades to StepIngredients automatically)
        - Create new RecipeIngredients from validated_data
        - Delete all old Steps (cascades to StepIngredients automatically)
        - Create new Steps and StepIngredients from validated_data
        """

        with transaction.atomic():
            # 1. Update recipe name
            instance.name = validated_data["name"]
            instance.save()

            # 2. Delete old ingredients and steps (this cascades to StepIngredients)
            instance.recipeingredient_set.all().delete()
            instance.recipe_steps.all().delete()

            # 3. Create/link ingredients (same logic as create)
            ingredient_map = {}

            for ingredient_data in validated_data["ingredients"]:
                # Get or create the base ingredient
                ingredient, _ = Ingredient.objects.get_or_create(
                    name=ingredient_data["name"]
                )

                # Create recipe ingredient link with amount/unit
                recipe_ingredient = RecipeIngredient.objects.create(
                    recipe=instance,
                    ingredient=ingredient,
                    amount=ingredient_data["amount"],
                    unit=ingredient_data.get("unit", ""),
                )

                # Store for step ingredient references
                ingredient_map[len(ingredient_map)] = recipe_ingredient

            # 4. Create steps and step-ingredient links (same logic as create)
            for step_data in validated_data["steps"]:
                step = Step.objects.create(
                    recipe=instance,
                    order=step_data["order"],
                    step=step_data["step"],
                )

                # Link ingredients to this step
                for step_ingredient_ref in step_data.get("ingredients", []):
                    ingredient_index = step_ingredient_ref["ingredient_index"]
                    recipe_ingredient = ingredient_map[ingredient_index]

                    StepIngredient.objects.create(
                        step=step, ingredient=recipe_ingredient
                    )

            return instance
