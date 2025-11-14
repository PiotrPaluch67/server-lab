# Hardened NGINX – Portfolio Edition
FROM nginx:alpine

# Run as non-root user
RUN adduser -D -H -s /sbin/nologin appuser
USER appuser

# Custom secure config
COPY nginx.conf /etc/nginx/nginx.conf
COPY index.html /usr/share/nginx/html/index.html

EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=3s \
  CMD wget --quiet --tries=1 --spider http://localhost:8080/ || exit 1