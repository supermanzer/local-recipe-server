# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Local Recipe Server is a self-hosted recipe management application using a 3-tier architecture:
- **Frontend**: Nuxt 3 (Vue 3 + Vuetify), running as an SPA (`ssr: false`), served via Nginx in production
- **Backend**: Django REST Framework API with JWT authentication
- **Database**: PostgreSQL with persistent volume
- **Orchestration**: Docker Compose with an Nginx gateway for routing and SSL termination

**Deployment:** Production runs on a DigitalOcean droplet (domain `myprivaterecipes.me`, see `gateway/nginx-ssl.conf`), fronted by Let's Encrypt certs mounted from `/etc/letsencrypt`. The `k8s/` directory at the project root is a **leftover from an earlier deployment attempt** targeting a Raspberry Pi cluster running microk8s — it is not used, not maintained, and can be ignored (or removed) safely.

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

`docker-compose.override.yml` is applied automatically alongside `docker-compose.yml` in local dev — it swaps the `nuxt` service from its production Nginx image for a `node:20` container running `npm run dev` (hot reload on port 3000→8900), and swaps in `nginx-ssl-dev.conf` so the gateway doesn't require Let's Encrypt certs locally.

### Django Management
```bash
docker-compose exec django2 python manage.py migrate          # Apply migrations
docker-compose exec django2 python manage.py makemigrations   # Create migrations
docker-compose exec django2 python manage.py shell            # Django shell
docker-compose exec django2 python manage.py dbshell          # PostgreSQL shell
docker-compose exec django2 python manage.py backup_recipes   # Backup all recipes
docker-compose exec django2 python manage.py restore_recipes <path> [--overwrite]  # Restore from backup
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
- `Recipe.steps` is a JSONField (legacy approach, coexists with the relational `Step` model — `RecipeBackup` still writes/reads it as `steps_json` but the app UI is driven entirely by the `Step`/`StepIngredient` models)
- StepIngredient allows highlighting which ingredients are used in each step
- Ingredient filtering uses AND logic: `/recipes/?ingredients=1&ingredients=2` returns recipes containing **both** ingredients

### Backend Architecture

**Django Project Structure:**
- `my_recipes/` - Main app with models, serializers, API views, backup logic, auth views
- `api/` - App containing URL routing (`api/urls.py`) and pagination config; note the ViewSets themselves live in `my_recipes/api_views.py`, not here
- `recipes/` - Project settings (settings.py, urls.py, wsgi.py, asgi.py)

**Key ViewSets** (`my_recipes/api_views.py`):
- `RecipeViewSet` - CRUD with ingredient/search filtering; swaps serializer class by action (see below)
- `IngredientViewSet` - Ingredient management
- Custom actions: `backup_recipes`, `restore_recipes`, `download_backup`

**Recipe Create & Update (`RecipeManageSerializer`):**
- `my_recipes/serializers.py` defines `RecipeManageSerializer`, a plain `serializers.Serializer` (not a `ModelSerializer`) used only for `create`/`update`/`partial_update` actions — `RecipeViewSet.get_serializer_class()` returns it for those actions and falls back to the read-only `RecipeSerializer` for `list`/`retrieve`.
- Both `.create()` and `.update()` run inside `transaction.atomic()` blocks and orchestrate writes across `Recipe`, `Ingredient` (via `get_or_create`), `RecipeIngredient`, `Step`, and `StepIngredient` in one call.
- **Update strategy is replace-all**: on update, all existing `RecipeIngredient` and `Step` rows for the recipe are deleted (cascades to `StepIngredient`) and recreated from the submitted payload — there is no partial/diff-based update.
- Steps reference their ingredients by **position**, not ID: the payload's `ingredients` list is flattened, and each step's `ingredients` array holds `{ ingredient_index: n }` pointing into that flattened list. The serializer builds an `ingredient_index -> RecipeIngredient` map while creating ingredients, then uses it to create `StepIngredient` links while creating steps.
- `RecipeViewSet.create()`/`update()` are overridden (not the default DRF behavior) to return the freshly saved recipe through the *read* `RecipeSerializer`, so API responses are always shaped consistently regardless of which serializer handled the write.

**Authentication:**
- JWT-based (`djangorestframework-simplejwt`), `IsAuthenticated` is the default DRF permission class
- Access tokens live 5 minutes (`SIMPLE_JWT.ACCESS_TOKEN_LIFETIME`), refresh tokens live 7 days
- `my_recipes/auth_views.py` defines a `register` view (`AllowAny`, creates a `User`), but **it is not wired into any `urlpatterns`** — there is currently no public self-service signup route. New users are created via `createsuperuser`/Django admin, or the bootstrap superuser described below.
- Superuser bootstrapped at container startup from `DJ_SUPERUSER`/`DJ_PASSWORD` env vars — see `django2/wait_for_db.sh`, which also waits for Postgres to accept connections and runs migrations before `exec`'ing the Dockerfile's `CMD`.

**Filtering & Search:**
- Uses `django-filter` with custom `RecipeFilterSet`
- Ingredient filter implements AND logic via `filter_ingredients_all` method
- Search fields: recipe name, ingredient names

### Frontend Architecture

**Nuxt 3 Structure** (all under `nuxt/recipe_client/`):
- `pages/` - Route-based components
  - `index.vue` - Recipe list with search and ingredient filtering
  - `recipes/[id].vue` - Recipe detail view
  - `recipes/new.vue` - Create-recipe route; thin wrapper rendering `<RecipesForm />`
  - `recipes/[id]-edit.vue` - Edit-recipe route; also just wraps `<RecipesForm />` (Nuxt resolves the `[id]` param, `Form.vue` handles create vs. edit internally)
  - `login.vue` - Authentication page
- `components/recipes/` - `Form.vue` (shared create/edit form), `CreateIngredients.vue`, `CreateSteps.vue`, `SearchBar.vue`, `ListView.vue`/`ListViewItem.vue`, `StepList.vue`/`StepListItem.vue`/`StepItem.vue`, `IngredientList.vue`/`IngredientListItem.vue`, `EditButton.vue`, `BackupRecipeButton.vue`, `RestoreRecipes.vue`
- `components/navigation/NavBar.vue`
- `composables/`
  - `recipeUtils.ts` - Recipe/ingredient API client (list, get, search, create, update, backup/restore/download, plus `convertRecipeToFormData()` which flattens an API `Recipe` back into the `RecipeCreatePayload` shape the form edits)
  - `useAuth.ts` - Token state (`useState`-backed), login/logout, localStorage persistence (`tokens` key), and `makeAuthRequest()` — the wrapper nearly every API call goes through
- `middleware/auth.ts` - Route middleware redirecting unauthenticated users to `/login`
- `plugins/auth.ts` - Calls `initAuth()` on app init to hydrate token state from localStorage
- `plugins/auth-handler.ts` - Provides a `$api` `$fetch` instance (`nuxtApp.$api`) whose `onResponse`/`onResponseError` hooks redirect to `/login` on 401/403
- `types/recipe.types.ts` - TypeScript definitions, including the `RecipeCreatePayload`/`RecipeIngredientInput`/`RecipeStepInput`/`StepIngredientReference` shapes used by the create/edit flow
- `nuxt.config.ts` - `ssr: false`, `runtimeConfig.public.baseURL` (from `API_BASE`), dev-only `nitro.devProxy` forwarding `/api/` to `http://django2:8000/api/`

**Auth token flow:** `useAuth.makeAuthRequest()` catches 401s, calls `refreshAccessToken()`, and retries the original request once; it also proactively schedules a refresh ~1 minute before the access token's `exp` claim (decoded client-side from the JWT) via `scheduleTokenRefresh()`. This is separate from, and in addition to, the reactive 401/403 handling in `plugins/auth-handler.ts`.

**API Integration:**
- `API_BASE` environment variable passed at build time (via `docker-compose.yml`'s `nuxt.build.args`)
- Build-time substitution ensures the correct API URL is baked into the static-generated assets (see `nuxt/Dockerfile`)
- Composables provide typed API methods; `useAuth.getErrorMessage()` normalizes DRF error payloads (detail/error/message/field errors/HTTP status) into user-facing strings

**Build Process:**
- Multi-stage Docker build: build stage (`node:latest`) runs `npm run generate` (static output, `ssr:false`), server stage (`nginx:stable-alpine`) serves the generated `dist/`
- Nginx serves on port 80 internally, exposed via the gateway on ports 80/443
- In local dev (`docker-compose.override.yml`), this whole build is bypassed in favor of `nuxt dev` in a `node:20` container with the source bind-mounted

### Backup & Restore

**Implementation:**
- `RecipeBackup` class in `my_recipes/backup.py` handles serialization/deserialization
- Saves to `MEDIA_ROOT` (django2/media directory)
- JSON format includes full recipe data with nested ingredients and steps (plus the legacy `steps_json` field for round-tripping)

**Workflow:**
1. User clicks backup button → POST `/api/recipes/backup_recipes/`
2. Django queries all recipes with relations → serializes to JSON
3. JSON file saved with timestamp naming
4. Optional restore: POST `/api/recipes/restore_recipes/` with file upload (`overwrite=true` replaces existing recipes matched by name; otherwise duplicates are skipped)
5. `GET /api/recipes/download_backup/` streams the most recently modified backup file in `MEDIA_ROOT`

## Environment Variables

All configured in `.env` file (not committed to git):

```env
# Django
DJ_SECRET_KEY=<value>           # Referenced in docs; settings.py actually reads DJ_KEY
DJ_KEY=<value>                  # Django SECRET_KEY (settings.py raises at startup if unset)
DJ_SUPERUSER=admin              # Initial admin username
DJ_PASSWORD=<secure>            # Initial admin password

# Database
POSTGRES_DB=recipes             # Database name
POSTGRES_USER=admin_user        # Database user
POSTGRES_PASSWORD=<secure>      # Database password
POSTGRES_PORT=5432

# CORS
NUXT_HOST=<value>               # Combined with NUXT_PORT to build an extra allowed CORS origin
NUXT_PORT=<value>

# API/Frontend
API_BASE=http://localhost:8585/api  # Frontend uses this to call backend; baked in at Nuxt build time
DATABASE_URL=<unused>                # Read from env in settings.py but not currently parsed into DATABASES
```

## Common Development Tasks

### Adding a New API Endpoint

1. Add logic to `my_recipes/models.py` if needed
2. Create/update serializer in `my_recipes/serializers.py`
3. Add ViewSet method in `my_recipes/api_views.py`
4. Register in URL routing via `api/urls.py`
5. Test with curl commands

### Changing Recipe Create/Update Behavior

Both flows share `RecipeManageSerializer` (`my_recipes/serializers.py`) and the frontend `Form.vue` component — changes to the payload shape need to stay in sync across:
- `RecipeManageSerializer` (backend validation/persistence)
- `RecipeCreatePayload` and related types in `nuxt/recipe_client/types/recipe.types.ts`
- `recipeUtils.convertRecipeToFormData()` (API → form shape, used when opening the edit form)

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
- Superuser created at startup via `wait_for_db.sh` entrypoint script
- JWT tokens generated upon login (`POST /api/token/`) and refreshed via `POST /api/token/refresh/`
- Requests to `/api/` endpoints require an `Authorization: Bearer <token>` header
- SimpleJWT library handles token generation/validation; frontend handles storage, proactive refresh, and 401/403 redirect-to-login (see Frontend Architecture above)

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
- `gateway/nginx.conf` reverse-proxies `/api|admin|static` to Django and everything else to Nuxt, on port 80
- `gateway/nginx-ssl.conf` (production) adds a port-443 server block with Let's Encrypt certs for `myprivaterecipes.me`; `gateway/nginx-ssl-dev.conf` is swapped in locally via `docker-compose.override.yml` so HTTPS/cert mounting isn't required for dev

## Testing Approach

- **Manual API Testing**: Use curl commands in the "API Testing" section
- **Database Validation**: Connect via psql and verify data integrity
- **Frontend Testing**: Visual testing in browser; check browser console for JS errors
- **Docker Health**: Check `docker-compose ps` and logs for startup issues
- Note: `django2/my_recipes/tests.py` exists but is currently the default empty Django test-file stub — there is no automated backend test suite yet.

## Important Notes

- **DEBUG Mode**: Currently enabled in `settings.py` (DEBUG=True). Disable in production.
- **ALLOWED_HOSTS**: Set to `["*"]` - should be restricted in production.
- **Secret Keys**: Must be configured via environment variables for production.
- **Volume Cleanup**: `docker-compose down -v` deletes the PostgreSQL data volume irreversibly.
- **Nuxt Build Time**: API_BASE must be set before build; changing it requires rebuild.
- **`k8s/` is legacy**: leftover manifests from an earlier Raspberry Pi/microk8s deployment attempt. Production hosting is now a DigitalOcean droplet via `docker-compose.yml` + the `gateway/` Nginx config. Don't extend or maintain the k8s manifests without checking with the project owner first.
- **Unwired `register` endpoint**: `my_recipes/auth_views.py:register` is dead code — not registered in any `urlpatterns`. If you're asked to add self-service signup, this is the natural starting point, but it needs a URL route added.
- **`tesseract-ocr`/`libtesseract-dev`** are installed in `django2/Dockerfile` but no OCR Python package (e.g. `pytesseract`) is in `requirements.txt` and no OCR code exists yet. This is intentional pre-provisioning: a long-term project goal is letting users upload a PDF or photo of a recipe and OCR it into structured ingredients/steps. Not scheduled yet — no plan or serializer/view work has started.

## Dependencies

- **Backend**: Django 6.0, DRF 3.16.1, SimpleJWT 5.5.1, django-filter, django-cors-headers, psycopg2-binary, Pillow, PyJWT, python-dotenv (Python 3.12, per `django2/Dockerfile`)
- **Frontend**: Nuxt 3.17.4, Vue 3.5.25, Vuetify 3.11.2, vue-router 4, @vueuse/nuxt, @nuxt/eslint, ESLint 9
- **Infrastructure**: PostgreSQL 15, Nginx, Docker Compose

## Directory Structure Quick Reference

```
django2/                    # Backend Django project
├── my_recipes/             # Core app: models, serializers, api_views, auth_views, backup, admin
│   ├── management/commands/  # backup_recipes, restore_recipes
│   └── migrations/
├── api/                     # URL routing (api/urls.py) + pagination classes
├── recipes/                 # Project settings, root urls, wsgi/asgi
├── manage.py
├── requirements.txt
├── Dockerfile               # Single-stage dev-oriented build
└── wait_for_db.sh           # Entrypoint: waits for Postgres, migrates, bootstraps superuser

nuxt/                        # Frontend
├── recipe_client/           # Nuxt app root
│   ├── pages/                # index.vue, login.vue, recipes/[id].vue, recipes/new.vue, recipes/[id]-edit.vue
│   ├── components/           # recipes/ (Form, CreateIngredients, CreateSteps, lists, backup/restore, ...), navigation/NavBar.vue
│   ├── composables/          # recipeUtils.ts, useAuth.ts
│   ├── middleware/auth.ts    # Redirects unauthenticated users to /login
│   ├── plugins/               # auth.ts (init), auth-handler.ts ($api with 401/403 redirect)
│   ├── types/recipe.types.ts
│   ├── layouts/default.vue
│   ├── nuxt.config.ts
│   └── package.json
├── Dockerfile                # Multi-stage: node build → nginx serve
└── nginx.conf                 # Nginx config for serving the static site

gateway/                      # Reverse-proxy/SSL termination in front of nuxt + django2
├── nginx.conf                # Port 80, routes /api|admin|static → django2, else → nuxt
├── nginx-ssl.conf             # Production HTTPS (Let's Encrypt, myprivaterecipes.me)
└── nginx-ssl-dev.conf         # Local dev substitute (no cert mounting required)

k8s/                          # LEGACY — Raspberry Pi/microk8s deployment attempt, superseded, unmaintained

docker-compose.yml            # Base orchestration (production-oriented: builds static Nuxt + nginx)
docker-compose.override.yml   # Local dev overrides (Nuxt dev server, dev SSL config)
.env                          # Environment variables (not in git)
README.md
```
