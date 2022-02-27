from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets

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

    def create(self, request):
        logger.info('Creating recipe from request: {}'.format(request))
        file_paths = request.data.get('files')
        text = create_recipe_json(file_paths)
        return Response(text)

    @action(detail=False, methods=["POST"], name="Confirm Recipe")
    def confirm_recipe(self, request, pk=None):
        recipe_data = request.data['recipe_json']
        recipe_id = create_recipe_records(recipe_data)
        return Response({'recipe_id': recipe_id})
