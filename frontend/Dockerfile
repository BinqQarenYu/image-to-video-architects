# Stage 1: Build the React application
FROM node:18-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
# We need to set the REACT_APP_BACKEND_URL for the build
# This will default to the docker-compose backend route if not provided
ARG REACT_APP_BACKEND_URL=http://localhost:8000
ENV REACT_APP_BACKEND_URL=$REACT_APP_BACKEND_URL
RUN npm run build

# Stage 2: Serve the app with Nginx
FROM nginx:alpine
# Copy the custom nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf
# Copy the built React app to nginx's html directory
COPY --from=build /app/build /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
