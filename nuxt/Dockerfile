#
# frontend_server/Dockerfile
# Define multi-stage build for front-end service
#

# Build stage
FROM node:latest AS build-stage

# Allow passing API_BASE at build time so `process.env.API_BASE` is
# available while running `npm run generate` (static generation).
ARG API_BASE
ENV API_BASE=${API_BASE}

RUN mkdir /app
WORKDIR /app
COPY recipe_client/package*.json /app/
RUN npm install --silent
COPY recipe_client .

# Use the environment variable during static generation so runtimeConfig
# public values that reference `process.env.API_BASE` are baked into the
# generated assets.
RUN npm run generate

# Server Stage
FROM nginx:stable-alpine
COPY --from=build-stage /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]