from logging import getLogger

from django.conf import settings
from django_filters import rest_framework as filters
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from my_recipes.backup import RecipeBackup

from .models import Ingredient, Recipe
from .serializers import IngredientSerializer, RecipeSerializer

logger = getLogger(__name__)


class RecipeFilterSet(filters.FilterSet):
    ingredients = filters.ModelMultipleChoiceFilter(
        queryset=Ingredient.objects.all(),
        method="filter_ingredients_all",
    )

    def filter_ingredients_all(self, queryset, name, value):
        """Filter recipes that have ALL selected ingredients (AND logic)"""
        if not value:
            return queryset

        # Start with all recipes
        filtered_queryset = queryset

        # For each ingredient, filter to only recipes containing it
        for ingredient in value:
            filtered_queryset = filtered_queryset.filter(ingredients=ingredient)

        return filtered_queryset

    class Meta:
        model = Recipe
        fields = ["ingredients"]


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    search_fields = ["name"]
    filterset_class = RecipeFilterSet
    ordering_fields = ["created_at", "modified_at", "name"]
    serializer_class = RecipeSerializer

    @action(detail=False, methods=["post"])
    def backup_recipes(self, request: Request):
        recipe_ids = request.data.get("recipes", None)
        output_dir = settings.MEDIA_ROOT
        try:
            RecipeBackup.backup_recipes(
                recipe_ids=recipe_ids, output_dir=output_dir
            )
            data, status = (
                {
                    "status": "success",
                    "message": f"Recipes backed up to {output_dir}",
                },
                200,
            )
        except Exception as e:
            data, status = {"error": str(e)}, 500

        return Response(data, status=status)

    @action(detail=False, methods=["post"])
    def restore_recipes(self, request: Request):
        backup_file = request.FILES.get("backup_file")
        overwrite = request.data("overwrite", False)

        if not backup_file:
            return Response({"error": "File missing"}, status=400)
        try:
            recipes = RecipeBackup.restore_recipes(
                input_file=backup_file, overwrite=overwrite
            )
            data, status = (
                {
                    "status": "success",
                    "message": f"Restored {len(recipes)} recipes",
                },
                200,
            )
        except Exception as e:
            data, status = {"error": str(e)}, 400

        return Response(data=data, status=status)


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    search_fields = ["name"]
    serializer_class = IngredientSerializer
