#
# frontend_server/Dockerfile
# Define multi-stage build for front-end service
#

# Build stage
FROM node:latest as build-stage
RUN mkdir /app
WORKDIR /app
COPY recipe_client/package*.json /app/
RUN npm install
COPY recipe_client . 
RUN npm run generate

# Server Stage
FROM nginx:stable-alpine
COPY --from=build-stage /app/dist /usr/share/nginx/html