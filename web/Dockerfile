# Build context is the repository root, where package-lock.json lives:
#   docker build -f web/Dockerfile -t latex-chat-web .

FROM node:24-alpine AS build
WORKDIR /app
# Manifests first, so the dependency layer is cached until they change
COPY package.json package-lock.json ./
COPY web/package.json web/
RUN npm ci --workspace web
COPY web/ web/
RUN npm run build --workspace web

# The final image has only nginx and the static files; it runs as a non-root user
FROM nginxinc/nginx-unprivileged:stable-alpine
COPY web/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/web/dist /usr/share/nginx/html
EXPOSE 8080
