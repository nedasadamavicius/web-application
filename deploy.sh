#!/bin/bash
set -e

echo "🗑 Clearing host static files..."
rm -rf /var/www/webapp/static
mkdir -p /var/www/webapp/static
chown -R http:http /var/www/webapp/static

echo "🐳 Rebuilding and starting Docker..."
docker compose -f docker-compose.prod.yml up --build -d

echo "🎨 Running collectstatic in the container..."
docker exec django_web_prod python3 manage.py collectstatic --noinput
echo "✅ Static files populated and container running."

echo "🔄 Restarting Nginx..."
systemctl restart nginx

echo "🚀 Deployment complete!"