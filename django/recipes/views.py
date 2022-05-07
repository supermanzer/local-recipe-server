from rest_framework import filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets


from django_filters import rest_framework as df_filters

from . import models, serializers

from .services.orchestration import create_recipe_json, create_recipe_records

from logging import getLogger

logger = getLogger(__name__)


class ImageViewSet(viewsets.ModelViewSet):
    queryset = models.Image.objects.all()
    serializer_class = serializers.ImageSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = models.Recipe.objects.all()
    serializer_class = serializers.RecipeSerializer
    search_fields = ['name', ]
    filterset_fields = ['ingredients', ]

    def create(self, request):
        files = list(request.data.pop('files'))

        # logger.info('File paths: {}'.format(files))
        text = create_recipe_json(files)
        return Response({'msg': "hello"})

    @action(detail=False, methods=["POST"], name="Confirm Recipe")
    def confirm(self, request, pk=None):
        logger.info('Confirming recipe: {}'.format(request.data))
        recipe_data = request.data['recipe_json']
        recipe_id = create_recipe_records(recipe_data)
        return Response({'recipe_id': recipe_id})


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = models.Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer
    search_fields = ['name', ]
