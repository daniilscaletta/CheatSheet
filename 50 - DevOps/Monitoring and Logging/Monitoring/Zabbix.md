#monitoring #DevOps 

Компоненты:

1) Zabbix-server
2) Zabbix-agent
3) Zabbix-proxy
4) БД
5) Web GUI

Модели мониторинга:
1) Пассивная:
	Agent <- **Server**
2) Активная (Сложнее)
	**Agent** -> Server

```yaml
services:

  postgres-server:
    image: postgres:latest
    restart: always
    volumes:
      - /var/lib/postgresql/data:/var/lib/postgresql/data
    environment:
      POSTGRES_USER: zabbix
      POSTGRES_PASSWORD: zabbix
      POSTGRES_DB: zabbix
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U zabbix"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - zbx-net

  zabbix-server:
    image: zabbix/zabbix-server-pgsql:alpine-latest
    ports:
      - "10051:10051"
    volumes:
      - /etc/localtime:/etc/localtime:ro
      - /etc/timezone:/etc/timezone:ro
      - /usr/lib/zabbix/alertscripts:/usr/lib/zabbix/alertscripts:ro
      - /usr/lib/zabbix/externalscripts:/usr/lib/zabbix/externalscripts:ro
      - /var/lib/zabbix/export:/var/lib/zabbix/export:rw
      - /var/lib/zabbix/modules:/var/lib/zabbix/modules:ro
      - /var/lib/zabbix/enc:/var/lib/zabbix/enc:ro
      - /var/lib/zabbix/ssh_keys:/var/lib/zabbix/ssh_keys:ro
      - /var/lib/zabbix/mibs:/var/lib/zabbix/mibs:ro
      - /var/lib/zabbix/snmptraps:/var/lib/zabbix/snmptraps:ro
    healthcheck:
      test: ["CMD-SHELL", "zabbix_server --help > /dev/null 2>&1"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s
    restart: always
    depends_on:
      postgres-server:
        condition: service_healthy
    environment:
      POSTGRES_USER: zabbix
      POSTGRES_PASSWORD: zabbix
      POSTGRES_DB: zabbix
      ZBX_HISTORYSTORAGETYPES: log,text
      ZBX_DEBUGLEVEL: 1
      ZBX_HOUSEKEEPINGFREQUENCY: 1
      ZBX_MAXHOUSEKEEPERDELETE: 5000
    networks:
      - zbx-net

  zabbix-web:
    image: zabbix/zabbix-web-nginx-pgsql:alpine-latest
    ports:
      - "8086:8080"
      - "8843:8443"
    volumes:
      - /etc/localtime:/etc/localtime:ro
      - /etc/timezone:/etc/timezone:ro
      - /etc/ssl/nginx:/etc/ssl/nginx:ro
      - /usr/share/zabbix/modules/:/usr/share/zabbix/modules/:ro
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/"]
      interval: 10s
      timeout: 5s
      retries: 3
      start_period: 30s
    sysctls:
      net.core.somaxconn: 65535
    restart: always
    depends_on:
      zabbix-server:
        condition: service_healthy
      postgres-server:
        condition: service_healthy
    environment:
      POSTGRES_USER: zabbix
      POSTGRES_PASSWORD: zabbix
      POSTGRES_DB: zabbix
      ZBX_SERVER_HOST: zabbix-server
      ZBX_POSTMAXSIZE: 64M
      PHP_TZ: Europe/Moscow
      ZBX_MAXEXECUTIONTIME: 500
    networks:
      - zbx-net

  zabbix-agent:
    image: zabbix/zabbix-agent:alpine-latest
    ports:
      - "10550:10550"
    volumes:
      - /etc/localtime:/etc/localtime:ro
      - /etc/timezone:/etc/timezone:ro
      - /proc:/proc
      - /sys:/sys
      - /dev:/dev
      - /var/run/docker.sock:/var/run/docker.sock
    privileged: true
    pid: "host"
    restart: always
    depends_on:
      zabbix-server:
        condition: service_healthy
    environment:
      ZBX_SERVER_HOST: zabbix-server
    networks:
      - zbx-net

networks:
  zbx-net:
    driver: bridge

```

Для Успешного подключения агента:

Monitoring -> Hosts -> Name - > Conf(Hosts) ->  DNS name (Как в Docker compose) -> Через 30 сек Available


### Установка плагина для мониторинга уязвимостей
[Репозиторий](https://github.com/SkillfactoryCoding/HACKER-LateralMovement-zabbix.threat.control)
