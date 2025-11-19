from logging import getLogger

from rest_framework import viewsets

from .models import Ingredient, Recipe
from .serializers import IngredientSerializer, RecipeSerializer

logger = getLogger(__name__)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    search_fields = ["name"]
    filterset_fields = [
        "ingredients",
    ]
    ordering_fields = ["created_at", "modified_at"]
    serializer_class = RecipeSerializer


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    search_fields = ["name"]
    serializer_class = IngredientSerializer
