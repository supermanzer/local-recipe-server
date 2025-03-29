"""
Define URL routing for the recipes application
"""

from django.urls import path
from recipes import views

app_name = "recipes"
urlpatterns = [path("", views.Index.as_view()), path("list", views.Recipes.as_view())]
