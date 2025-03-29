from django.views import generic
from recipes.models import Recipe


class Index(generic.TemplateView):
    template_name = "recipes/index.html"


class Recipes(generic.ListView):
    model = Recipe
    template_name = "recipes/recipe_list.html"
    context_object_name = "recipes"
