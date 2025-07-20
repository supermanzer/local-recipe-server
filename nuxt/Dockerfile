#
# frontend_server/Dockerfile
# Define multi-stage build for front-end service
#

# Build stage
FROM arm64v8/node:latest AS build-stage
RUN mkdir /app
WORKDIR /app
COPY recipe_client/package*.json /app/
RUN npm install --silent
COPY recipe_client . 
RUN npm run generate

# Server Stage
FROM arm64v8/nginx:stable-alpine
COPY --from=build-stage /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]