from django.urls import path, include
from rest_framework import routers
from recipes import views

router = routers.DefaultRouter()

# Register API endpoints that map to models
router.register(r'images', views.ImageViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
