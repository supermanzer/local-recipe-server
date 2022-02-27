from django.urls import path, include
from rest_framework import routers
from recipes import views

router = routers.DefaultRouter()

# Register API endpoints that map to models
# router.register(r'images', views.ImageViewSet)
router.register(r'recipes', views.RecipeViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
