from django.urls import path

from . import views

urlpatterns = [
    path("recipes/", views.RecipeListView.as_view(), name="recipes"),
    path("info/", views.InformationView.as_view(), name="info"),
    path("", views.IndexView.as_view(), name="index"),
]
