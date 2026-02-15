# Recipe Creation & Editing Feature Implementation Plan

## Overview

This document outlines the implementation strategy for adding recipe creation and editing functionality to the Local Recipe Server. The feature will enable users to:
- **Create** new recipes with ingredients, steps, and step-ingredient relationships
- **Edit** existing recipes, modifying ingredients, steps, and step-ingredient relationships

The same form and API endpoints handle both operations (POST for create, PUT for update).

## Architecture Overview

The implementation follows REST API best practices with a pragmatic approach to handling complex nested object creation and updates. The same form component and serializer handle both operations:

```
Frontend (Nuxt)          Backend (Django)         Database
┌──────────────┐         ┌──────────────┐         ┌──────────────┐
│ RecipeForm   │─POST──→ │ RecipeViewSet│─────→   │ Recipe       │
│ Page         │         │ (create)     │         │ Ingredient   │
│ (create or   │         └──────────────┘         │ RecipeIngr   │
│  edit mode)  │                                  │ Step         │
│              │─PUT──→  │ RecipeViewSet│─────→   │ StepIngredient
└──────────────┘         │ (update)     │         └──────────────┘
   ↓                            ↓
 Form data              Validates & processes
   ↓                            ↓
 Step-ingredient              Transaction
 relationships         (atomic all-or-nothing)
```

**Key difference**:
- **Create (POST)**: Create new Recipe, all new RecipeIngredients, all new Steps
- **Update (PUT)**: Preserve Recipe ID, replace ingredients/steps (delete old, create new), maintain referential integrity

## Phase 1: Backend Implementation

### 1.1 Update Type Definitions in Models

The existing models support this feature. Key points:
- `Recipe.name` - already exists
- `Recipe.ingredients` - M2M through `RecipeIngredient` ✓
- `Step` model - already has `recipe` FK and `order` field ✓
- `StepIngredient` - already links steps to recipe ingredients ✓

**No model changes needed** - architecture is already in place.

### 1.2 Create Write Serializers for Recipe Creation

**File**: `django2/my_recipes/serializers.py`

Your existing serializers already use DRF's `ModelSerializer` with built-in `.create()` and `.update()` methods. For recipe creation, we'll create a specialized serializer to handle the nested creation workflow:

```python
# Existing serializers (already implemented):
# - RecipeIngredientSerializer (ModelSerializer - read from RecipeIngredient model)
# - StepSerializer (ModelSerializer - read from Step model)
# - StepIngredientSerializer (ModelSerializer - read from StepIngredient model)
# - RecipeSerializer (ModelSerializer - read from Recipe model)

# New serializers for creation (NOT ModelSerializers - custom structure):
class IngredientInputSerializer(serializers.Serializer):
    """Input serializer for ingredient data during recipe creation"""
    name = serializers.CharField(max_length=200)
    amount = serializers.DecimalField(max_digits=5, decimal_places=2)
    unit = serializers.CharField(max_length=200, required=False, allow_blank=True)

class StepIngredientReferenceSerializer(serializers.Serializer):
    """References an ingredient by its index in the ingredients list"""
    ingredient_index = serializers.IntegerField(min_value=0)
    # ingredient_index maps to the ingredient at ingredients[index]

class StepInputSerializer(serializers.Serializer):
    """Input serializer for step data during recipe creation"""
    order = serializers.IntegerField(min_value=1)
    step = serializers.CharField()
    ingredients = StepIngredientReferenceSerializer(many=True, required=False)

class RecipeManageSerializer(serializers.Serializer):
    """
    Handles both recipe creation and updating with nested ingredients and steps.

    This is a regular Serializer (not ModelSerializer) because the structure
    doesn't directly map to a model. Both .create() and .update() methods
    orchestrate operations across multiple related models in atomic transactions.
    """
    id = serializers.IntegerField(required=False, read_only=True)  # Present only on update
    name = serializers.CharField(max_length=200)
    ingredients = IngredientInputSerializer(many=True)
    steps = StepInputSerializer(many=True)

    def create(self, validated_data):
        """
        Override .create() to handle recipe creation with nested objects.

        Process:
        1. Create Recipe instance with name
        2. For each ingredient:
           - Get or create Ingredient record
           - Create RecipeIngredient record (linking ingredient to recipe with amount/unit)
        3. For each step:
           - Create Step record (linked to recipe with order)
           - For each step ingredient reference:
             - Create StepIngredient record (linking step to recipe ingredient)

        All operations wrapped in transaction.atomic() for consistency.
        Returns the created Recipe instance.
        """
        # Implementation in Phase 1.4
        pass

    def update(self, instance, validated_data):
        """
        Override .update() to handle recipe editing with nested objects.

        For updates, we preserve the Recipe ID but replace all related objects.
        This approach is simpler than trying to patch individual relationships.

        Process:
        1. Update Recipe.name if changed
        2. Delete all existing RecipeIngredients for this recipe
        3. Create new RecipeIngredients from validated_data
        4. Delete all existing Steps for this recipe
        5. Create new Steps and StepIngredients from validated_data

        All operations wrapped in transaction.atomic() for consistency.
        Returns the updated Recipe instance.
        """
        # Implementation in Phase 1.4
        pass
```

**Design rationale**:
- `RecipeManageSerializer` is a regular `Serializer` (not `ModelSerializer`) because the structure doesn't directly map to a model
- Both `.create()` and `.update()` methods follow DRF patterns you're already using
- Nested serializers validate individual components (ingredients, steps)
- `ingredient_index` approach avoids ID lookups on frontend
- Nested structure mirrors the UI form structure
- Single atomic request prevents partial data creation
- Update strategy: replace all related objects (simpler than trying to patch individual relationships)
  - Delete old RecipeIngredients/Steps and create new ones
  - Maintains referential integrity in one atomic transaction
  - No orphaned records or partial updates

### 1.3 Implement RecipeViewSet for Create and Update Operations

**File**: `django2/my_recipes/api_views.py`

Update the existing `RecipeViewSet` to use different serializers for create/update vs. read operations. This follows the DRF pattern you're already using with `ModelViewSet`:

```python
from django.db import transaction
from rest_framework import status

class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer  # Default for list/retrieve
    permission_classes = [IsAuthenticated]
    # ... existing code (backup_recipes, restore_recipes, etc.) ...

    def get_serializer_class(self):
        """
        Use RecipeManageSerializer for POST (create) and PUT/PATCH (update).
        Use RecipeSerializer for list/retrieve (read-only).

        This follows DRF best practice of using different serializers for
        different operations.
        """
        if self.action in ('create', 'update', 'partial_update'):
            return RecipeManageSerializer
        return RecipeSerializer

    def create(self, request, *args, **kwargs):
        """
        Override create to handle validation and response for new recipes.

        Flow:
        1. Use RecipeManageSerializer to validate nested data
        2. Call serializer.save() which runs serializer.create()
        3. All database operations in serializer.create() are atomic
        4. Return created recipe using read serializer (RecipeSerializer)
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # serializer.create() does all the work (see Phase 1.4)
        recipe = serializer.save()

        # Return using read serializer for full recipe data
        read_serializer = RecipeSerializer(recipe)
        return Response(read_serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        """
        Override update to handle validation and response for recipe edits.

        Flow:
        1. Get existing recipe instance
        2. Use RecipeManageSerializer to validate nested data
        3. Call serializer.save(instance=recipe) which runs serializer.update()
        4. All database operations in serializer.update() are atomic
        5. Return updated recipe using read serializer (RecipeSerializer)
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)

        # serializer.update() does all the work (see Phase 1.4)
        recipe = serializer.save()

        # Return using read serializer for full recipe data
        read_serializer = RecipeSerializer(recipe)
        return Response(read_serializer.data, status=status.HTTP_200_OK)
```

**Pattern note**: This follows DRF best practice - different serializers for different operations (read vs. write), with `.create()` and `.update()` overrides in the serializer itself, just as you're already doing with your existing serializers.

### 1.4 Implementation Details for RecipeManageSerializer.create() and .update()

**Following Your Existing DRF Pattern:**

Your serializers already override `.create()` and `.update()` when needed. `RecipeManageSerializer` follows the same pattern - it's a regular `Serializer` (not `ModelSerializer`) with custom `.create()` and `.update()` methods to handle the complex multi-model operations:

```python
# This is the same pattern you're using now, just for a more complex case
class RecipeManageSerializer(serializers.Serializer):
    # ... field definitions ...

    def create(self, validated_data):
        # Business logic for creating Recipe + related objects
        # This will be called automatically by viewset.create() via serializer.save()
        pass

    def update(self, instance, validated_data):
        # Business logic for updating Recipe + related objects
        # This will be called automatically by viewset.update() via serializer.save()
        pass
```

**Detailed Implementation for .create():

```python
def create(self, validated_data):
    """
    Detailed implementation of atomic recipe creation.

    Key considerations:
    - Ingredient reuse: get_or_create() handles existing ingredients
    - Amount/unit tracking: stored on RecipeIngredient, not Ingredient
    - Step ordering: provided by frontend
    - Step-ingredient linking: uses ingredient_index to reference items
    """

    with transaction.atomic():
        # 1. Create recipe
        recipe = Recipe.objects.create(name=validated_data['name'])

        # 2. Create/link ingredients
        ingredient_map = {}  # Maps ingredient_index → RecipeIngredient ID

        for ingredient_data in validated_data['ingredients']:
            # Get or create the base ingredient
            ingredient, _ = Ingredient.objects.get_or_create(
                name=ingredient_data['name']
            )

            # Create recipe ingredient link with amount/unit
            recipe_ingredient = RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient,
                amount=ingredient_data['amount'],
                unit=ingredient_data.get('unit', '')
            )

            # Store for step ingredient references
            ingredient_map[len(ingredient_map)] = recipe_ingredient

        # 3. Create steps and step-ingredient links
        for step_data in validated_data['steps']:
            step = Step.objects.create(
                recipe=recipe,
                order=step_data['order'],
                step=step_data['step']
            )

            # 4. Link ingredients to this step
            for step_ingredient_ref in step_data.get('ingredients', []):
                ingredient_index = step_ingredient_ref['ingredient_index']
                recipe_ingredient = ingredient_map[ingredient_index]

                StepIngredient.objects.create(
                    step=step,
                    ingredient=recipe_ingredient
                )

        return recipe
```

**Detailed Implementation for .update():**

```python
def update(self, instance, validated_data):
    """
    Detailed implementation of atomic recipe updates.

    Strategy: Replace all related objects (RecipeIngredients and Steps).
    This is simpler than patching individual relationships and ensures
    consistency - we know exactly what ingredients and steps exist after update.

    Key considerations:
    - Preserve Recipe ID (the instance parameter)
    - Update Recipe.name if changed
    - Delete all old RecipeIngredients (cascades to StepIngredients automatically)
    - Create new RecipeIngredients from validated_data
    - Delete all old Steps (cascades to StepIngredients automatically)
    - Create new Steps and StepIngredients from validated_data
    """

    with transaction.atomic():
        # 1. Update recipe name
        instance.name = validated_data['name']
        instance.save()

        # 2. Delete old ingredients and steps (this cascades to StepIngredients)
        instance.recipeingredient_set.all().delete()
        instance.recipe_steps.all().delete()

        # 3. Create/link ingredients (same logic as create)
        ingredient_map = {}

        for ingredient_data in validated_data['ingredients']:
            # Get or create the base ingredient
            ingredient, _ = Ingredient.objects.get_or_create(
                name=ingredient_data['name']
            )

            # Create recipe ingredient link with amount/unit
            recipe_ingredient = RecipeIngredient.objects.create(
                recipe=instance,
                ingredient=ingredient,
                amount=ingredient_data['amount'],
                unit=ingredient_data.get('unit', '')
            )

            # Store for step ingredient references
            ingredient_map[len(ingredient_map)] = recipe_ingredient

        # 4. Create steps and step-ingredient links (same logic as create)
        for step_data in validated_data['steps']:
            step = Step.objects.create(
                recipe=instance,
                order=step_data['order'],
                step=step_data['step']
            )

            # Link ingredients to this step
            for step_ingredient_ref in step_data.get('ingredients', []):
                ingredient_index = step_ingredient_ref['ingredient_index']
                recipe_ingredient = ingredient_map[ingredient_index]

                StepIngredient.objects.create(
                    step=step,
                    ingredient=recipe_ingredient
                )

        return instance
```

**Why the "replace all" strategy for updates:**
- **Simplicity**: Easier to reason about - no partial update issues
- **Consistency**: Ingredient indices in the request always work (don't need to track which IDs changed)
- **Safety**: No orphaned records or partial updates if something fails
- **Performance**: Single atomic operation rather than multiple patch operations
- **Foreign keys**: StepIngredient cascading deletes automatically clean up old step-ingredient links

**Error handling** (both create and update):
- `ValueError` if `ingredient_index` is out of range → invalid request
- Ingredient name conflicts handled by `get_or_create()`
- Duplicate step orders allowed (UI responsibility to maintain uniqueness)
- Transaction rolls back on any database error
- 404 if recipe not found (handled by viewset.get_object())

### 1.5 API Endpoints

Both create and update use the standard DRF endpoints with the same request format:

**Create Recipe (POST `/api/recipes/`):**

```bash
curl -X POST http://localhost:8585/api/recipes/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "name": "Pasta Carbonara",
    "ingredients": [
      {"name": "Spaghetti", "amount": 400, "unit": "g"},
      {"name": "Eggs", "amount": 3, "unit": ""},
      {"name": "Bacon", "amount": 200, "unit": "g"},
      {"name": "Parmesan", "amount": 100, "unit": "g"}
    ],
    "steps": [
      {
        "order": 1,
        "step": "Boil water and cook spaghetti",
        "ingredients": [{"ingredient_index": 0}]
      },
      {
        "order": 2,
        "step": "Fry bacon until crispy",
        "ingredients": [{"ingredient_index": 2}]
      },
      {
        "order": 3,
        "step": "Mix eggs with parmesan",
        "ingredients": [{"ingredient_index": 1}, {"ingredient_index": 3}]
      },
      {
        "order": 4,
        "step": "Combine pasta, bacon, and egg mixture",
        "ingredients": [{"ingredient_index": 0}, {"ingredient_index": 2}, {"ingredient_index": 1}]
      }
    ]
  }'
```

**Response (201 Created)**: Full recipe data using RecipeSerializer format

---

**Update Recipe (PUT `/api/recipes/{id}/`):**

Same request format as create, updates the entire recipe with new ingredients and steps:

```bash
curl -X PUT http://localhost:8585/api/recipes/1/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "name": "Pasta Carbonara (Updated)",
    "ingredients": [
      {"name": "Spaghetti", "amount": 500, "unit": "g"},
      {"name": "Eggs", "amount": 4, "unit": ""},
      {"name": "Guanciale", "amount": 250, "unit": "g"},
      {"name": "Pecorino", "amount": 150, "unit": "g"}
    ],
    "steps": [
      {"order": 1, "step": "Boil salted water...", "ingredients": [{"ingredient_index": 0}]},
      {"order": 2, "step": "Fry guanciale...", "ingredients": [{"ingredient_index": 2}]},
      {"order": 3, "step": "Whisk eggs with pecorino...", "ingredients": [{"ingredient_index": 1}, {"ingredient_index": 3}]},
      {"order": 4, "step": "Combine everything...", "ingredients": [{"ingredient_index": 0}, {"ingredient_index": 2}]}
    ]
  }'
```

**Response (200 OK)**: Updated recipe data using RecipeSerializer format

**Note**: Update replaces all ingredients and steps. Any ingredients/steps not in the request are deleted.

---

## Phase 2: Frontend Implementation

### 2.1 Update Type Definitions

**File**: `nuxt/recipe_client/types/recipe.types.ts`

Add new types for the recipe management form (used for both create and update):

```typescript
// Add these new types for recipe creation/edit form

export interface RecipeIngredientInput {
    name: string;
    amount: number;
    unit: string;
}

export interface StepIngredientReference {
    ingredient_index: number;
}

export interface RecipeStepInput {
    order: number;
    step: string;
    ingredients: StepIngredientReference[];
}

export interface RecipeCreatePayload {
    name: string;
    ingredients: RecipeIngredientInput[];
    steps: RecipeStepInput[];
}
```

**Important**: When loading an existing recipe for editing, the API returns `RecipeSerializer` format (which has `id`, `name`, `ingredients`, `recipe_steps`). You'll need to convert this to `RecipeCreatePayload` format in the frontend before populating the form:

```typescript
// Conversion function (helper in manage.vue or composable)
const convertRecipeToFormData = (recipe: Recipe): RecipeCreatePayload => {
    return {
        name: recipe.name,
        ingredients: recipe.ingredients.map(ing => ({
            name: ing.name,
            amount: parseFloat(ing.amount),
            unit: ing.unit || ''
        })),
        steps: recipe.recipe_steps.map(step => ({
            order: step.order,
            step: step.step,
            ingredients: step.step_ingredients.map((si, idx) => ({
                ingredient_index: recipe.ingredients.findIndex(
                    ing => ing.id === si.ingredient.id
                )
            }))
        }))
    };
};
```

### 2.2 Add API Methods to recipeUtils

**File**: `nuxt/recipe_client/composables/recipeUtils.ts`

Add three new methods for recipe creation, updating, and deletion:

```typescript
const createRecipe = async (recipeData: RecipeCreatePayload): Promise<Recipe> => {
    const url = '/recipes/'
    const response = await makeAuthRequest<Recipe>(url, "POST", recipeData)
    return response
}

const updateRecipe = async (recipeId: number, recipeData: RecipeCreatePayload): Promise<Recipe> => {
    const url = `/recipes/${recipeId}/`
    const response = await makeAuthRequest<Recipe>(url, "PUT", recipeData)
    return response
}

const deleteRecipe = async (recipeId: number): Promise<void> => {
    const url = `/recipes/${recipeId}/`
    await makeAuthRequest<void>(url, "DELETE")
}

// Add to return statement:
return {
    getRecipes,
    getRecipe,
    searchRecipes,
    getIngredients,
    triggerBackup,
    triggerRestore,
    downloadLatestBackup,
    createRecipe,   // NEW
    updateRecipe,   // NEW
    deleteRecipe    // NEW
}
```

**Note**: `deleteRecipe` uses the standard DRF DELETE method (no custom implementation needed)

### 2.3 Create Recipe Management Page (Create & Edit)

**File**: `nuxt/recipe_client/pages/recipes/manage.vue` (or `nuxt/recipe_client/pages/create.vue`)

The form handles both create (POST) and edit (PUT) operations based on route parameters. The same component works for both modes:

```vue
<template>
  <div class="recipe-manage-container">
    <h1>{{ isEditMode ? 'Edit Recipe' : 'Create New Recipe' }}</h1>

    <!-- Recipe Name Input -->
    <v-text-field
      v-model="form.name"
      label="Recipe Name"
      required
    />

    <!-- Ingredients Section -->
    <RecipeCreateIngredients
      v-model="form.ingredients"
    />

    <!-- Steps Section -->
    <RecipeCreateSteps
      v-model="form.steps"
      :ingredients="form.ingredients"
    />

    <!-- Action Buttons -->
    <v-btn @click="submitRecipe" :loading="isSubmitting">
      {{ isEditMode ? 'Update Recipe' : 'Create Recipe' }}
    </v-btn>
    <v-btn @click="$router.back()">
      Cancel
    </v-btn>

    <!-- Delete button (edit mode only) -->
    <v-btn
      v-if="isEditMode"
      @click="deleteRecipe"
      color="error"
      :loading="isDeleting"
    >
      Delete Recipe
    </v-btn>
  </div>
</template>

<script setup lang="ts">
import type { RecipeCreatePayload } from '~/types/recipe.types';

definePageMeta({
    name: "ManageRecipe",
    middleware: 'auth'
});

const route = useRoute();
const recipeId = route.params.id ? parseInt(route.params.id as string) : null;
const isEditMode = !!recipeId;

const form = ref<RecipeCreatePayload>({
    name: '',
    ingredients: [],
    steps: []
});

const isSubmitting = ref(false);
const isDeleting = ref(false);
const { createRecipe, updateRecipe, getRecipe, deleteRecipe: deleteRecipeAPI } = recipeUtils();

// Load recipe if editing
onMounted(async () => {
    if (isEditMode && recipeId) {
        const recipe = await getRecipe(recipeId.toString());
        // Populate form with existing recipe data
        form.value.name = recipe.name;
        form.value.ingredients = recipe.ingredients; // Convert from RecipeSerializer format
        form.value.steps = recipe.recipe_steps; // Convert from StepSerializer format
    }
});

const submitRecipe = async () => {
    // Validate form
    // Call createRecipe() or updateRecipe()
    // Handle success/error
    // Redirect to recipe detail
};

const deleteRecipe = async () => {
    if (!isEditMode || !recipeId) return;

    // Confirm deletion
    // Call deleteRecipeAPI()
    // Redirect to recipes list
};
</script>
```

**Route structure**:
- `POST /create` - Create new recipe (no ID)
- `PUT /recipes/[id]` - Edit existing recipe (with ID in URL)

### 2.4 Create Ingredient Input Component

**File**: `nuxt/recipe_client/components/recipes/CreateIngredients.vue`

Features:
- Add/remove ingredient rows dynamically
- Input fields for: name, amount, unit
- Client-side validation (name required, amount > 0)
- Display all ingredients with edit/delete buttons

```vue
<template>
  <v-card>
    <v-card-title>Ingredients</v-card-title>

    <v-list>
      <v-list-item
        v-for="(ingredient, index) in modelValue"
        :key="index"
      >
        <!-- Ingredient inputs -->
        <v-text-field
          v-model="ingredient.name"
          label="Ingredient Name"
          density="compact"
        />
        <v-text-field
          v-model.number="ingredient.amount"
          label="Amount"
          type="number"
          density="compact"
        />
        <v-text-field
          v-model="ingredient.unit"
          label="Unit (optional)"
          density="compact"
        />
        <v-btn
          icon="mdi-delete"
          @click="removeIngredient(index)"
        />
      </v-list-item>
    </v-list>

    <v-btn @click="addIngredient" prepend-icon="mdi-plus">
      Add Ingredient
    </v-btn>
  </v-card>
</template>

<script setup lang="ts">
interface Ingredient {
    name: string;
    amount: number;
    unit: string;
}

const props = defineProps<{ modelValue: Ingredient[] }>();
const emit = defineEmits(['update:modelValue']);

const addIngredient = () => {
    emit('update:modelValue', [
        ...props.modelValue,
        { name: '', amount: 0, unit: '' }
    ]);
};

const removeIngredient = (index: number) => {
    emit('update:modelValue',
        props.modelValue.filter((_, i) => i !== index)
    );
};
</script>
```

### 2.5 Create Steps Input Component

**File**: `nuxt/recipe_client/components/recipes/CreateSteps.vue`

Features:
- Add/remove step rows dynamically
- Order field (auto-assigned or user-set)
- Step text editor
- Multi-select for ingredients used in this step
- Visual confirmation of ingredient selection

```vue
<template>
  <v-card>
    <v-card-title>Steps</v-card-title>

    <v-list>
      <v-list-item
        v-for="(step, index) in modelValue"
        :key="index"
      >
        <v-text-field
          v-model.number="step.order"
          label="Order"
          type="number"
          density="compact"
          style="max-width: 100px"
        />
        <v-textarea
          v-model="step.step"
          label="Step Instructions"
          density="compact"
          counter
          maxlength="1000"
        />

        <!-- Ingredient Selection -->
        <v-autocomplete
          v-model="selectedIngredients[index]"
          :items="ingredientOptions"
          label="Ingredients used in this step"
          multiple
          chips
          @update:modelValue="updateStepIngredients(index, $event)"
        />

        <v-btn
          icon="mdi-delete"
          @click="removeStep(index)"
        />
      </v-list-item>
    </v-list>

    <v-btn @click="addStep" prepend-icon="mdi-plus">
      Add Step
    </v-btn>
  </v-card>
</template>

<script setup lang="ts">
interface Ingredient {
    name: string;
    amount: number;
    unit: string;
}

interface Step {
    order: number;
    step: string;
    ingredients: Array<{ ingredient_index: number }>;
}

const props = defineProps<{
    modelValue: Step[];
    ingredients: Ingredient[];
}>();

const emit = defineEmits(['update:modelValue']);

const selectedIngredients = ref<number[][]>(
    props.modelValue.map(step =>
        step.ingredients.map(ing => ing.ingredient_index)
    )
);

const ingredientOptions = computed(() =>
    props.ingredients.map((ing, index) => ({
        title: `${ing.name} (${ing.amount} ${ing.unit})`,
        value: index
    }))
);

const updateStepIngredients = (stepIndex: number, ingredientIndices: number[]) => {
    const updated = [...props.modelValue];
    updated[stepIndex].ingredients = ingredientIndices.map(idx => ({
        ingredient_index: idx
    }));
    emit('update:modelValue', updated);
};

const addStep = () => {
    const newOrder = Math.max(...props.modelValue.map(s => s.order), 0) + 1;
    emit('update:modelValue', [
        ...props.modelValue,
        { order: newOrder, step: '', ingredients: [] }
    ]);
};

const removeStep = (index: number) => {
    emit('update:modelValue',
        props.modelValue.filter((_, i) => i !== index)
    );
};
</script>
```

### 2.6 Update Navigation

**NavBar**: Add link to create new recipe:

```vue
<!-- In NavBar.vue -->
<v-btn
  to="/create"
  prepend-icon="mdi-plus"
>
  New Recipe
</v-btn>
```

**Recipe Detail Page**: Add link to edit recipe (if you have a recipe detail page):

```vue
<!-- In recipes/[id].vue or similar -->
<v-btn
  :to="`/recipes/${recipe.id}/edit`"
  prepend-icon="mdi-pencil"
>
  Edit
</v-btn>
```

---

## Phase 3: Form Validation & Error Handling

### 3.1 Frontend Validation

```typescript
// In create.vue
const validateForm = (): string[] => {
    const errors: string[] = [];

    if (!form.value.name.trim()) {
        errors.push('Recipe name is required');
    }

    if (form.value.ingredients.length === 0) {
        errors.push('At least one ingredient is required');
    }

    form.value.ingredients.forEach((ing, idx) => {
        if (!ing.name.trim()) {
            errors.push(`Ingredient ${idx + 1}: name is required`);
        }
        if (ing.amount <= 0) {
            errors.push(`Ingredient ${idx + 1}: amount must be greater than 0`);
        }
    });

    if (form.value.steps.length === 0) {
        errors.push('At least one step is required');
    }

    form.value.steps.forEach((step, idx) => {
        if (!step.step.trim()) {
            errors.push(`Step ${idx + 1}: instruction text is required`);
        }
    });

    return errors;
};
```

### 3.2 Backend Validation

- DRF serializers handle basic field validation
- Business logic validation in `RecipeCreateSerializer.validate()`
- Database constraints enforce referential integrity
- Transaction ensures consistency

### 3.3 Error Handling Flow

```
Frontend Submit
    ↓
[Validate locally]
    ├─ Errors? → Show error toast
    └─ OK? ↓
[POST to API]
    ↓
[Validate in serializer]
    ├─ Errors? → HTTP 400 with error details
    └─ OK? ↓
[Process transaction]
    ├─ Error? → HTTP 500 with error message
    └─ Success? ↓
[Return created recipe]
    ↓
[Frontend shows success]
[Navigate to recipe detail]
```

---

## Phase 4: User Experience Considerations

### 4.1 Form State Management

Use Vue 3 composable for form management:

```typescript
const useRecipeForm = () => {
    const form = ref({
        name: '',
        ingredients: [],
        steps: []
    });

    const addIngredient = () => { /* ... */ };
    const removeIngredient = (index: number) => { /* ... */ };
    const addStep = () => { /* ... */ };
    const removeStep = (index: number) => { /* ... */ };

    const reset = () => {
        form.value = { name: '', ingredients: [], steps: [] };
    };

    return { form, addIngredient, removeIngredient, addStep, removeStep, reset };
};
```

### 4.2 Responsive Design

- Mobile: Single column, collapsible sections
- Tablet: Two columns for ingredients/steps
- Desktop: Full sidebar layout

### 4.3 Performance Optimization

- Lazy load component at `/create` route
- Use `v-if` for step ingredient selection (only show when ingredients exist)
- Debounce autocomplete searches
- Validate on blur, not on every keystroke

### 4.4 Accessibility

- Proper label associations with form fields
- ARIA labels for ingredient indices
- Keyboard navigation support
- Clear focus indicators

---

## Phase 5: Testing Strategy

### Backend Tests

```python
# tests/test_recipe_management.py

class RecipeManagementTestCase(TestCase):

    # CREATE TESTS
    def test_create_recipe_with_new_ingredients(self):
        """Recipe creation creates new ingredients"""
        data = {
            "name": "Pasta",
            "ingredients": [
                {"name": "Pasta", "amount": 400, "unit": "g"}
            ],
            "steps": [
                {"order": 1, "step": "Boil water", "ingredients": []}
            ]
        }
        response = self.client.post('/api/recipes/', data)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Recipe.objects.filter(name="Pasta").exists())
        self.assertTrue(Ingredient.objects.filter(name="Pasta").exists())

    def test_create_recipe_reuses_existing_ingredients(self):
        """Recipe creation reuses existing ingredients"""
        # Setup: Create an ingredient first
        Ingredient.objects.create(name="Salt")

        data = {
            "name": "Soup",
            "ingredients": [
                {"name": "Salt", "amount": 1, "unit": "tsp"}
            ],
            "steps": [{"order": 1, "step": "Add salt", "ingredients": []}]
        }
        response = self.client.post('/api/recipes/', data)

        # Verify ingredient wasn't duplicated
        self.assertEqual(Ingredient.objects.filter(name="Salt").count(), 1)

    def test_create_recipe_with_step_ingredients(self):
        """Recipe creation links steps to ingredients"""
        data = {
            "name": "Recipe",
            "ingredients": [
                {"name": "Ingredient1", "amount": 1, "unit": ""},
                {"name": "Ingredient2", "amount": 2, "unit": ""}
            ],
            "steps": [
                {
                    "order": 1,
                    "step": "First step",
                    "ingredients": [{"ingredient_index": 0}]
                }
            ]
        }
        response = self.client.post('/api/recipes/', data)

        step = Step.objects.first()
        self.assertEqual(step.stepingredient_set.count(), 1)

    def test_create_recipe_atomic_transaction(self):
        """Recipe creation rolls back on error"""
        data = {
            "name": "Recipe",
            "ingredients": [
                {"name": "Ing", "amount": "invalid", "unit": ""}  # Invalid
            ],
            "steps": []
        }
        response = self.client.post('/api/recipes/', data)

        self.assertEqual(response.status_code, 400)
        self.assertFalse(Recipe.objects.filter(name="Recipe").exists())

    # UPDATE TESTS
    def test_update_recipe_changes_name(self):
        """Recipe update changes the recipe name"""
        recipe = Recipe.objects.create(name="Original")
        Ingredient.objects.create(name="Salt")
        ing = Ingredient.objects.get(name="Salt")
        RecipeIngredient.objects.create(recipe=recipe, ingredient=ing, amount=1, unit="tsp")
        Step.objects.create(recipe=recipe, order=1, step="Do something")

        data = {
            "name": "Updated Name",
            "ingredients": [{"name": "Salt", "amount": 2, "unit": "tsp"}],
            "steps": [{"order": 1, "step": "Do something else", "ingredients": []}]
        }
        response = self.client.put(f'/api/recipes/{recipe.id}/', data)
        self.assertEqual(response.status_code, 200)

        recipe.refresh_from_db()
        self.assertEqual(recipe.name, "Updated Name")

    def test_update_recipe_replaces_ingredients(self):
        """Recipe update deletes old ingredients and creates new ones"""
        recipe = Recipe.objects.create(name="Recipe")
        old_ing = Ingredient.objects.create(name="OldIngredient")
        RecipeIngredient.objects.create(recipe=recipe, ingredient=old_ing, amount=1, unit="")

        data = {
            "name": "Recipe",
            "ingredients": [{"name": "NewIngredient", "amount": 2, "unit": "g"}],
            "steps": []
        }
        response = self.client.put(f'/api/recipes/{recipe.id}/', data)
        self.assertEqual(response.status_code, 200)

        # Old ingredient link removed, new one created
        self.assertEqual(recipe.recipeingredient_set.count(), 1)
        self.assertTrue(recipe.ingredients.filter(name="NewIngredient").exists())
        self.assertFalse(recipe.ingredients.filter(name="OldIngredient").exists())

    def test_update_recipe_replaces_steps(self):
        """Recipe update deletes old steps and creates new ones"""
        recipe = Recipe.objects.create(name="Recipe")
        Step.objects.create(recipe=recipe, order=1, step="Old step")

        data = {
            "name": "Recipe",
            "ingredients": [],
            "steps": [{"order": 1, "step": "New step", "ingredients": []}]
        }
        response = self.client.put(f'/api/recipes/{recipe.id}/', data)
        self.assertEqual(response.status_code, 200)

        # Old step removed, new one created
        self.assertEqual(recipe.recipe_steps.count(), 1)
        self.assertTrue(recipe.recipe_steps.filter(step="New step").exists())
        self.assertFalse(recipe.recipe_steps.filter(step="Old step").exists())

    def test_update_recipe_atomic_transaction(self):
        """Recipe update rolls back on error"""
        recipe = Recipe.objects.create(name="Recipe")
        original_name = recipe.name

        data = {
            "name": "Updated",
            "ingredients": [
                {"name": "Ing", "amount": "invalid", "unit": ""}  # Invalid
            ],
            "steps": []
        }
        response = self.client.put(f'/api/recipes/{recipe.id}/', data)

        self.assertEqual(response.status_code, 400)
        recipe.refresh_from_db()
        self.assertEqual(recipe.name, original_name)  # Name not changed due to rollback
```

### Frontend Tests

- Unit tests for form validation
- Component tests for input fields
- Integration tests for API calls
- E2E tests for complete workflow

---

## Implementation Order (Recommended)

1. **Backend Phase 1**: Serializers and viewset (2-3 hours)
   - ✓ No model changes needed
   - Create `RecipeManageSerializer` with both `.create()` and `.update()` methods
   - Override `RecipeViewSet.get_serializer_class()`, `.create()`, and `.update()` methods

2. **Frontend Phase 2**: Type definitions and API integration (30-45 minutes)
   - Add input types for form data
   - Add conversion helper for reading existing recipes
   - Add `createRecipe()`, `updateRecipe()`, `deleteRecipe()` to recipeUtils

3. **Frontend Phase 3**: Form page and components (3-4 hours)
   - Create unified form page (handles both create and edit modes)
   - Ingredient component
   - Steps component
   - Form data loading and population (for edit mode)
   - Navigation links (create button and edit links)

4. **Testing & Refinement**: (1-2 hours)
   - Backend tests (create and update)
   - Frontend validation
   - Error handling
   - Edit mode specific testing
   - UX polish

**Total estimated time**: 7-10 hours

---

## Key Design Decisions

| Decision | Rationale | Alternative |
|----------|-----------|-------------|
| **Separate RecipeCreateSerializer** | Different request structure than response; keeps read/write separated (DRF best practice you already follow) | Reuse RecipeSerializer for both (violates SoC) |
| **Override .create() in serializer** | Standard DRF pattern you're already using; keeps business logic in serializer | Override viewset.create() (mixed concerns) |
| **Nested serializers (non-model)** | Validate components individually; request structure != response structure | Single flat serializer (less validation) |
| **ingredient_index references** | No ID lookup needed on frontend, simpler form structure | Pre-create ingredients endpoint (multiple requests) |
| **Single POST endpoint** | RESTful, atomic, prevents partial records | Separate endpoints per resource (harder to keep in sync) |
| **Transaction.atomic()** | Ensures consistency, no orphaned records | Manual rollback (error-prone) |
| **v-model component pattern** | Idiomatic Vue 3, proper reactivity | Direct array manipulation (imperative) |

---

## Potential Future Enhancements

- Recipe templates/duplication feature
- Bulk ingredient import from URL/text
- Recipe tags/categories
- Ingredient substitutions
- Cooking time/difficulty estimates
- Recipe versioning/history
- Collaborative recipe editing

---

## References

- DRF Documentation: https://www.django-rest-framework.org/
- Nuxt 3 Documentation: https://nuxt.com/
- Vue 3 Composition API: https://vuejs.org/guide/extras/composition-api-faq.html
- REST API Design Best Practices: https://restfulapi.net/
