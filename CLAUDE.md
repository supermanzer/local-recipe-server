# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Local Recipe Server is a self-hosted recipe management application using a 3-tier architecture:
- **Frontend**: Nuxt 3 (Vue 3 + Vuetify) served via Nginx
- **Backend**: Django REST Framework API with JWT authentication
- **Database**: PostgreSQL with persistent volume
- **Orchestration**: Docker Compose with Nginx gateway for SSL support

## Quick Start Commands

### Docker
```bash
docker-compose up -d              # Start all services
docker-compose down               # Stop all services
docker-compose ps                 # Check running services
docker-compose logs -f <service>  # View service logs (django2, nuxt, postgres, gateway)
docker-compose down -v            # Full reset (deletes persistent data)
docker-compose up -d --build      # Rebuild images
```

### Django Management
```bash
docker-compose exec django2 python manage.py migrate          # Apply migrations
docker-compose exec django2 python manage.py makemigrations   # Create migrations
docker-compose exec django2 python manage.py shell            # Django shell
docker-compose exec django2 python manage.py dbshell          # PostgreSQL shell
docker-compose exec django2 python manage.py backup_recipes   # Backup all recipes
```

### Nuxt Frontend
```bash
docker-compose exec nuxt bash                    # Enter container
npm install                                      # Install dependencies
npm run dev                                      # Run dev server
npm run generate                                 # Static site generation
npm run lint                                     # Run ESLint
npm run lint:fix                                 # Fix linting issues
```

### API Testing
```bash
# Get all recipes (requires authentication - see JWT handling below)
curl http://localhost:8585/api/recipes/

# Filter recipes by ingredients (AND logic - returns recipes with ALL selected ingredients)
curl 'http://localhost:8585/api/recipes/?ingredients=1&ingredients=2'

# Access Django admin
# http://localhost:8585/admin (credentials from .env DJ_SUPERUSER/DJ_PASSWORD)

# Access frontend
# http://localhost:8900

# Access gateway (includes SSL support if configured)
# http://localhost (ports 80/443)
```

## Architecture Deep Dive

### Data Model

The core entities and their relationships:

```
Recipe
├── ingredients (M2M via RecipeIngredient)
└── recipe_steps (1:N with Step)

Ingredient (unique by name)

RecipeIngredient (through table)
├── recipe (FK)
├── ingredient (FK)
├── amount (DecimalField)
└── unit (CharField)

Step
├── recipe (FK)
├── order (PositiveInteger)
└── step (TextField)

StepIngredient (links steps to recipe ingredients)
├── step (FK)
└── ingredient (FK to RecipeIngredient)
```

**Important Notes:**
- `Recipe.steps` is a JSONField (legacy approach, check for dual implementation with Step model)
- StepIngredient allows highlighting which ingredients are used in each step
- Ingredient filtering uses AND logic: `/recipes/?ingredients=1&ingredients=2` returns recipes containing **both** ingredients
- All data model relationships are complete, although the Recipe model does implement the legacy steps field.

### Backend Architecture

**Django Project Structure:**
- `my_recipes/` - Main app with models (Recipe, Ingredient, Step, RecipeIngredient, StepIngredient)
- `api/` - Contains ViewSets, serializers, and URL routing
- `recipes/` - Project settings (settings.py, urls.py, wsgi.py)

**Key ViewSets:**
- `RecipeViewSet` - CRUD operations with filtering by ingredients and search
- `IngredientViewSet` - Ingredient management
- Custom actions: `backup_recipes`, `restore_recipes`, `download_backup`

**Authentication:**
- JWT-based (SimpleJWT library in requirements)
- `IsAuthenticated` permission class on ViewSets
- Credentials created at startup via environment variables

**Filtering & Search:**
- Uses `django-filter` with custom `RecipeFilterSet`
- Ingredient filter implements AND logic via `filter_ingredients_all` method
- Search fields: recipe name, ingredient names

### Frontend Architecture

**Nuxt 3 Structure:**
- `pages/` - Route-based components
  - `index.vue` - Recipe list with search and filtering
  - `recipes/[id].vue` - Recipe detail view
  - `login.vue` - Authentication page
- `components/recipes/` - Reusable recipe components
  - SearchBar, ListView, StepList, IngredientList, BackupRecipeButton, RestoreRecipes
- `composables/recipeUtils.ts` - API client and request utilities
- `types/recipe.types.ts` - TypeScript type definitions
- `nuxt.config.ts` - Nuxt configuration with `runtimeConfig.public.apiBase`

**API Integration:**
- `API_BASE` environment variable passed at build time (via docker-compose.yml)
- Build-time substitution ensures correct API URL in static-generated assets
- RecipeUtils composable provides API methods with error handling

**Build Process:**
- Multi-stage Docker build: build stage generates static site, server stage serves with Nginx
- `npm run generate` creates static HTML (required for production build)
- Nginx serves on port 80 internally, exposed via gateway on ports 80/443

### Backup & Restore

**Implementation:**
- `RecipeBackup` class in `my_recipes/backup.py` handles serialization
- Saves to `MEDIA_ROOT` (django2/media directory)
- JSON format includes full recipe data with nested ingredients and steps

**Workflow:**
1. User clicks backup button → POST `/api/recipes/backup_recipes/`
2. Django queries all recipes with relations → serializes to JSON
3. JSON file saved with timestamp naming
4. Optional restore: POST `/api/recipes/restore_recipes/` with file upload
5. Restore parses JSON and creates/updates all records

## Environment Variables

All configured in `.env` file (not committed to git):

```env
# Django
DJ_SECRET_KEY=<value>           # Django SECRET_KEY
DJ_KEY=<value>                  # Alternative key name (used in settings)
DJ_SUPERUSER=admin              # Initial admin username
DJ_PASSWORD=<secure>            # Initial admin password

# Database
POSTGRES_DB=recipes             # Database name
POSTGRES_USER=admin_user        # Database user
POSTGRES_PASSWORD=<secure>      # Database password
POSTGRES_PORT=5432

# API/Frontend
API_BASE=http://localhost:8585/api  # Frontend uses this to call backend
DATABASE_URL=<auto-generated>       # Constructed from POSTGRES_* variables
```

## Common Development Tasks

### Adding a New API Endpoint

1. Add logic to `my_recipes/models.py` if needed
2. Create/update serializer in `my_recipes/serializers.py`
3. Add ViewSet method in `my_recipes/api_views.py`
4. Register in URL routing via `api/urls.py`
5. Test with curl commands

### Running Database Migrations

```bash
# After model changes
docker-compose exec django2 python manage.py makemigrations my_recipes
docker-compose exec django2 python manage.py migrate

# Verify migration status
docker-compose exec django2 python manage.py showmigrations
```

### Debugging API Issues

```bash
docker-compose logs -f django2   # Watch Django logs
docker-compose exec django2 python manage.py shell  # Interactive debugging
curl -v http://localhost:8585/api/recipes/         # Verbose HTTP debugging
```

### Frontend Development

Run dev server for hot-reload:
```bash
docker-compose exec nuxt npm run dev
```

Then access frontend at the exposed dev server URL. Note: This runs within the container and may require port forwarding.

## Key Implementation Details

**Authentication Flow:**
- Superuser created at startup via entrypoint script
- JWT tokens generated upon login
- Requests to /api/ endpoints require `Authorization: Bearer <token>` header
- SimpleJWT library handles token generation/validation

**Ingredient Filtering:**
- Each ingredient in query params is an additional filter (AND logic)
- `filter_ingredients_all()` in RecipeFilterSet implements this via loop-based filtering
- Example: `?ingredients=1&ingredients=2` returns only recipes with ingredients 1 AND 2

**Search Implementation:**
- Uses DRF's SearchFilter on recipe name field
- Frontend SearchBar component collects user input and triggers API call
- Search is case-insensitive (handled by Django's ORM)

**Media/Backup Storage:**
- Backups saved to `django2/media/` directory (mounted in Docker)
- Persisted across container restarts (not in named volume for easy access)
- Backup filenames include timestamp for sorting

**Gateway/Nginx:**
- Reverse proxy routes requests to Nuxt and Django services
- SSL support via letsencrypt volumes (configured for production deployment)
- Handles CORS at gateway level if needed

## Testing Approach

- **Manual API Testing**: Use curl commands in the "API Testing" section
- **Database Validation**: Connect via psql and verify data integrity
- **Frontend Testing**: Visual testing in browser; check browser console for JS errors
- **Docker Health**: Check `docker-compose ps` and logs for startup issues

## Important Notes

- **DEBUG Mode**: Currently enabled in `settings.py` (DEBUG=True). Disable in production.
- **ALLOWED_HOSTS**: Set to `["*"]` - should be restricted in production.
- **Secret Keys**: Must be configured via environment variables for production.
- **Volume Cleanup**: `docker-compose down -v` deletes the PostgreSQL data volume irreversibly.
- **Nuxt Build Time**: API_BASE must be set before build; changing it requires rebuild.

## Dependencies

- **Backend**: Django 6.0, DRF 3.16.1, SimpleJWT 5.5.1, psycopg2, django-filter, django-cors-headers
- **Frontend**: Nuxt 3.17.4, Vue 3.5.25, Vuetify 3.11.2, ESLint
- **Infrastructure**: PostgreSQL 15, Nginx, Docker

## Directory Structure Quick Reference

```
django2/              # Backend Django project
├── my_recipes/       # Core app (models, serializers, views, backup logic)
├── api/              # API routing
├── recipes/          # Project settings
├── manage.py
├── requirements.txt
└── Dockerfile

nuxt/                 # Frontend
├── recipe_client/    # Nuxt app root
│   ├── pages/        # Route components
│   ├── components/   # Reusable Vue components
│   ├── composables/  # API utilities
│   ├── types/        # TypeScript definitions
│   ├── layouts/
│   ├── nuxt.config.ts
│   └── package.json
├── Dockerfile
└── nginx.conf        # Nginx configuration for serving static site

docker-compose.yml    # Orchestration config
.env                  # Environment variables (not in git)
gateway/nginx.conf    # Gateway reverse proxy config
```
