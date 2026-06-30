FROM serversideup/php:8.4-fpm-nginx

# Switch to root to modify permissions if needed
USER root

# Set the document root for Nginx
ENV WEB_DOCUMENT_ROOT=/var/www/html/public

# Copy application files
COPY . /var/www/html

# Ensure proper ownership of all Laravel files so Composer can run
RUN chown -R www-data:www-data /var/www/html

# Switch back to the standard non-root user
USER www-data

# Install Composer dependencies
RUN composer install --no-dev --optimize-autoloader --no-interaction
