FROM nginx:1.29

# Copy the built application files to the Nginx HTML directory
COPY --chown=root:root --chmod=0644 ./app /usr/share/nginx/html

# Periodically check if the Nginx service is running
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD [ "service", "nginx", "status", "||", "exit", "1" ]
