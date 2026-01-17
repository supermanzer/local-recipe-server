# Gemini Code Assistant Project Overview: Recipe Server

This document provides a comprehensive overview of the `local-recipe-server` project, a multi-container web application designed for storing, managing, and sharing recipes.

## Project Overview

The application is a full-stack recipe management system. It allows authenticated users to create, view, edit, and delete their recipes. Key features include a rich text editor for recipe instructions, ingredient management, and the ability to back up and restore the recipe database from a file. The frontend is a modern, responsive single-page application (SPA) that communicates with a backend REST API.

## Architecture

The system is designed using a microservices-oriented architecture, orchestrated with Docker Compose. This separates concerns between the frontend, backend, and database, making the application scalable and maintainable.

The main services are:

1.  **`gateway` (Nginx):** Acts as a reverse proxy and the main entry point for all incoming web traffic. It is configured to route requests to the appropriate frontend or backend service. It's also set up to handle SSL termination using Let's Encrypt certificates managed by Certbot.

2.  **`nuxt` (Frontend):** A Nuxt.js (Vue.js framework) application that provides the user interface. It is built as a static site and served by Nginx. It communicates with the Django backend via RESTful API calls. The UI is built with the Vuetify component library for a Material Design look and feel.

3.  **`django2` (Backend):** A Django application that serves a REST API built with the Django REST Framework (DRF). It handles all business logic, including:
    *   User authentication (using JWT).
    *   CRUD (Create, Read, Update, Delete) operations for recipes and ingredients.
    *   Advanced filtering and searching of recipes.
    *   Recipe backup and restore functionality.
    *   Potential for OCR (Optical Character Recognition) with Tesseract, as indicated by the installed dependencies.

4.  **`postgres` (Database):** A PostgreSQL database that serves as the persistent data store for the Django backend. All recipe data, user information, and ingredients are stored here.

5.  **`certbot`:** A container that automatically manages SSL certificates from Let's Encrypt to enable HTTPS for the application.

## Technologies Used

*   **Backend:**
    *   Python / Django / Django REST Framework
    *   PostgreSQL (with `psycopg2-binary`)
    *   JWT for authentication (`djangorestframework_simplejwt`)
    *   Tesseract OCR (dependency included)
*   **Frontend:**
    *   JavaScript / Nuxt.js / Vue.js
    *   Vuetify (Material Design Component Framework)
    *   Nginx (to serve static content)
*   **DevOps & Orchestration:**
    *   Docker & Docker Compose
    *   Nginx (as a reverse proxy gateway)
    *   Certbot (for SSL/TLS)

## Project Structure

The project is organized into several directories, each corresponding to a service or a logical part of the application.

```
/
├── docker-compose.yml      # Main Docker Compose file to orchestrate all services.
├── django2/                # Contains the Django backend application.
│   ├── Dockerfile          # Dockerfile for the backend service.
│   ├── manage.py           # Django's command-line utility.
│   ├── my_recipes/         # The core Django app for recipes.
│   │   ├── api_views.py    # API views (REST endpoints).
│   │   ├── models.py       # Database models (Recipe, Ingredient, etc.).
│   │   └── urls.py         # URL routing for the my_recipes app.
│   ├── recipes/            # Django project settings and configuration.
│   └── requirements.txt    # Python dependencies.
├── nuxt/                   # Contains the Nuxt.js frontend application.
│   ├── Dockerfile          # Dockerfile for the frontend service.
│   ├── nginx.conf          # Nginx configuration for serving the Nuxt app.
│   └── recipe_client/      # The Nuxt.js source code.
│       ├── components/     # Vue components.
│       ├── pages/          # Application pages and routing.
│       ├── nuxt.config.ts  # Nuxt.js configuration.
│       └── package.json    # Node.js dependencies.
├── certbot/                # Configuration and data for Certbot/SSL.
├── gateway/                # (Assumed) Nginx gateway configuration.
└── ...
```

## How to Run the Application

The application is designed to be run with Docker Compose.

1.  **Environment Variables:** Create a `.env` file in the project root directory. This file should contain necessary environment variables such as `API_BASE` for the Nuxt build, and database credentials (`POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`) for the Django and Postgres services.

2.  **Build and Run:** From the project root, run the following command:
    ```bash
    docker-compose up --build
    ```
    This command will build the Docker images for the `nuxt` and `django2` services and then start all the containers defined in `docker-compose.yml`.

3.  **Accessing the App:** Once the containers are running, the application should be accessible in your web browser at `http://localhost`. The Nginx gateway will route you to the Nuxt.js frontend, which will then make API calls to the Django backend.
