FROM nginx:alpine

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy frontend files to nginx html directory
COPY . /usr/share/nginx/html

# Expose port
EXPOSE 3000

# Start nginx with daemon off
CMD ["nginx", "-g", "daemon off;"]