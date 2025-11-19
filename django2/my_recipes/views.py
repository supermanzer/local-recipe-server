from django.shortcuts import render
from django.views import generic

from .models import Recipe


class RecipeListView(generic.ListView):
    model = Recipe
    template_name = "my_recipes/recipe_list.html"


class RecipeDetailView(generic.DetailView):
    model = Recipe
    template_name = "my_recipes/recipe_detail.html"


class InformationView(generic.View):
    template_name = "my_recipes/info.html"

    def get(self, request):
        return render(request, self.template_name)


class IndexView(generic.View):
    template_name = "my_recipes/index.html"

    def get(self, request):
        return render(request, self.template_name)
