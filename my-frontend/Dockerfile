# Build stage
FROM node:20-alpine as build

# Install system dependencies
RUN apk update && apk add \
    git 

WORKDIR /app
RUN git clone https://github.com/charlesuland/StatisticsDashboard.git
RUN mv StatisticsDashboard/my-frontend/* . && rm -rf StatisticsDashboard

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
