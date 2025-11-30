from logging import getLogger

from django_filters import rest_framework as filters
from rest_framework import viewsets

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


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    search_fields = ["name"]
    serializer_class = IngredientSerializer
