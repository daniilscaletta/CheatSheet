
```yaml

services:
  nginx:
    image: nginx:1.24-alpine
    container_name: nginx_production
    hostname: nginx-prod
    
    ports:
      - "80:80"
      - "443:443"
    networks:
      - frontend
      - backend
        
    env_file: .env
	environment:    
      - NGINX_HOST=${NGINX_HOST:-127.0.0.1}
      - NGINX_PORT=${NGINX_PORT:-80}
      - TZ=${TZ:-Europe/Moscow}

    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/conf.d/:/etc/nginx/conf.d/:ro
      - ./nginx/snippets/:/etc/nginx/snippets/:ro
      - ./static:/var/www/static:ro
      - ./uploads:/var/www/uploads:rw
      - ./logs/nginx:/var/log/nginx
      - ./html:/usr/share/nginx/html:ro
    
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:80/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '1.0'
    
    
networks:
  frontend:
    driver: bridge
  backend:
    driver: bridge
```