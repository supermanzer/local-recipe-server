from django.contrib import admin

from .models import Ingredient, Recipe, RecipeIngredient, Step, StepIngredient


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient

    extra = 1


class StepIngredientInline(admin.TabularInline):
    model = StepIngredient

    extra = 1


class StepInline(admin.TabularInline):
    model = Step

    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ["name", "recipe_ingredients"]

    inlines = [RecipeIngredientInline, StepInline]


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    pass


@admin.register(Step)
class StepAdmin(admin.ModelAdmin):
    inlines = [StepIngredientInline]


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    inlines = [StepIngredientInline]
