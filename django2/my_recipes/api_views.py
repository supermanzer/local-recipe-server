from logging import getLogger
from pathlib import Path

from django.conf import settings
from django.http import FileResponse
from django_filters import rest_framework as filters
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from my_recipes.backup import RecipeBackup

from .models import Ingredient, Recipe
from .serializers import (
    IngredientSerializer,
    RecipeManageSerializer,
    RecipeSerializer,
)

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
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        """
        Use RecipeManageSerializer for POST (create) and PUT/PATCH (update).
        Use RecipeSerializer for list/retrieve (read-only).

        This follows DRF best practice of using different serializers for
        different operations.
        """
        if self.action in ("create", "update", "partial_update"):
            return RecipeManageSerializer
        return RecipeSerializer

    def create(self, request, *args, **kwargs):
        """
        Override create to handle validation and response for new recipes.

        Flow:
        1. Use RecipeManageSerializer to validate nested data
        2. Call serializer.save() which runs serializer.create()
        3. All database operations in serializer.create() are atomic
        4. Return created recipe using read serializer (RecipeSerializer)
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # serializer.create() does all the work (see Phase 1.4)
        recipe = serializer.save()

        # Return using read serializer for full recipe data
        read_serializer = RecipeSerializer(recipe)
        return Response(read_serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        """
        Override update to handle validation and response for recipe edits.

        Flow:
        1. Get existing recipe instance
        2. Use RecipeManageSerializer to validate nested data
        3. Call serializer.save(instance=recipe) which runs serializer.update()
        4. All database operations in serializer.update() are atomic
        5. Return updated recipe using read serializer (RecipeSerializer)
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)

        # serializer.update() does all the work (see Phase 1.4)
        recipe = serializer.save()

        # Return using read serializer for full recipe data
        read_serializer = RecipeSerializer(recipe)
        return Response(read_serializer.data, status=status.HTTP_200_OK)

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
            data, status = {"status": "failed", "error": str(e)}, 500

        return Response(data, status=status)

    @action(detail=False, methods=["post"])
    def restore_recipes(self, request: Request):
        backup_file = request.FILES.get("backup_file")
        overwrite = request.data.get("overwrite", False)

        if not backup_file:
            return Response(
                {"status": "failed", "error": "File missing"}, status=400
            )
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

    @action(detail=False, methods=["get"])
    def download_backup(self, request: Request):
        """Download the latest backup file from media root"""
        try:
            media_root = Path(settings.MEDIA_ROOT)
            logger.info("Searching for latest backup file in media root")

            # Find all backup files matching the pattern
            backup_files = sorted(
                media_root.glob("recipes_backup_*.json"),
                key=lambda x: x.stat().st_mtime,
                reverse=True,
            )

            if not backup_files:
                logger.warning("No backup files found in media root")
                return Response(
                    {"status": "failed", "error": "No backup files found"},
                    status=404,
                )

            latest_backup = backup_files[0]
            logger.info(f"Found latest backup: {latest_backup.name}")

            # Open and return the file
            response = FileResponse(
                open(latest_backup, "rb"),
                as_attachment=True,
                filename=latest_backup.name,
            )
            logger.info(f"Sending backup file: {latest_backup.name}")
            return response

        except Exception as e:
            logger.error(f"Error downloading backup: {str(e)}")
            return Response({"status": "failed", "error": str(e)}, status=500)


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    search_fields = ["name"]
    serializer_class = IngredientSerializer
    permission_classes = [IsAuthenticated]
