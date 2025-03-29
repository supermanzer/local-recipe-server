from django.urls import path, include
from rest_framework import routers
from recipes import api_views

router = routers.DefaultRouter()

# Register API endpoints that map to models
# router.register(r'images', views.ImageViewSet)
router.register(r"recipes", api_views.RecipeViewSet)
router.register(r"ingredients", api_views.IngredientViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
