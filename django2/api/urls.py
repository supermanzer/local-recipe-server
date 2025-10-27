from my_recipes import api_views
from rest_framework import routers

from django.urls import include, path

router = routers.DefaultRouter()

router.register(r"recipes", api_views.RecipeViewSet)
router.register(r"ingredients", api_views.IngredientViewSet)

urlpatterns = [path("", include(router.urls))]
