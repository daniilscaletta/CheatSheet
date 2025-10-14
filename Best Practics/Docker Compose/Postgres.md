```yaml

services:

	postgres:
		container_name: postgres
		image: postgres:15
		restart: unless-stopped
		env_file: .env
		environment:
			- POSTGRES_USER=${POSTGRES_USER:-user}
			- POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-pass}
			- POSTGRES_DB=${POSTGRES_DB:-db}
		volumes:
			- db_data:/var/lib/postgresql/data
		networks:
			- network
		healthcheck:
			test: ["CMD-SHELL", "pg_isready"]
			interval: 5s
			timeout: 5s
			retries: 5
	
volumes:
	db_data:

networks:
	network:
```
