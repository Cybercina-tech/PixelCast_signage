# Production image — build from repository root:
#   docker build -f frontend/Dockerfile .
#
# Stage 1: Build the Vue.js application
FROM node:20-alpine AS builder

WORKDIR /app

RUN apk add --no-cache git

COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ .
RUN npm run build

# Stage 2: Serve with Nginx
FROM nginx:alpine

RUN apk add --no-cache wget

COPY --from=builder /app/dist /usr/share/nginx/html

COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
