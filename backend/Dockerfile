FROM serversideup/php:8.3-fpm-nginx

# Switch to root to modify permissions if needed
USER root

# Set the document root for Nginx
ENV WEB_DOCUMENT_ROOT=/var/www/html/public

# Copy application files
COPY . /var/www/html

# Ensure proper ownership of Laravel writable directories
RUN chown -R www-data:www-data /var/www/html/storage \
    && chown -R www-data:www-data /var/www/html/bootstrap/cache \
    && chown -R www-data:www-data /var/www/html/database

# Switch back to the standard non-root user
USER www-data

# Install Composer dependencies
RUN composer install --no-dev --optimize-autoloader --no-interaction
