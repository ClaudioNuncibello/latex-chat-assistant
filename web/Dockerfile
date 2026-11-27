# Build context is this folder:
#   docker build -t latex-chat-web web

FROM node:24-alpine AS build
WORKDIR /app
# Manifests first, so the dependency layer is cached until they change
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

# The final image has only nginx and the static files; it runs as a non-root user
FROM nginxinc/nginx-unprivileged:stable-alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 8080
