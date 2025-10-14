```yaml

services:

  redis:
    image: redis:7.2-alpine
    container_name: redis
    restart: unless-stopped
    env_file:
		- .env
	networks:
		- network
		  
networks:
	network:
```