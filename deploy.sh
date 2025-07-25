#!/bin/bash
set -e

echo "DEBUG: SPOTIFY_ENV_PATH = $SPOTIFY_ENV_PATH"

echo "🗑 Clearing host static files..."
rm -rf /var/www/webapp/static
mkdir -p /var/www/webapp/static
chown -R http:http /var/www/webapp/static

echo "🐳 Rebuilding and starting Docker..."
docker compose -f docker-compose.prod.yml up --build -d

echo "🎨 Running collectstatic in the container..."
docker exec django_web_prod python3 manage.py collectstatic --noinput
echo "✅ Static files populated and container running."

echo "🔄 Applying database migrations..."
docker exec django_web_prod python3 manage.py migrate --noinput
echo "🔄 Database migrations applied."

echo "🔄 Restarting Nginx..."
systemctl restart nginx

echo "🚀 Deployment complete!"