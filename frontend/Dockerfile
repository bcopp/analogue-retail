# Build stage
FROM node:18-alpine as build

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY . .

# Build the app
RUN npm run build

# Production stage
FROM nginx:alpine

# Create directory for SSL certificates
RUN mkdir -p /etc/nginx/ssl

# Copy SSL certificates
COPY ssl/tls.crt /etc/nginx/ssl/tls.crt
COPY ssl/tls.key /etc/nginx/ssl/tls.key

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built files
COPY --from=build /app/build /usr/share/nginx/html

# Expose both HTTP and HTTPS ports
EXPOSE 80 443

# Start nginx
CMD ["nginx", "-g", "daemon off;"] 