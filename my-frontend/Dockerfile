# Build stage
FROM node:20-alpine as build
WORKDIR /app
COPY package.json package-lock.json* ./
COPY . .
RUN npm ci --prefer-offline --no-audit --progress=false
RUN npm run build

# Production stage
FROM nginx:stable-alpine
COPY --from=build /app/dist /usr/share/nginx/html
# Remove default nginx.conf and use a simple one that serves SPA
RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
