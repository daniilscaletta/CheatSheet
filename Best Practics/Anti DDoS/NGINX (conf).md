#ddos #nginx 

nginx.conf
```yml
user www-data;
worker_processes auto;                # использует все ядра CPU
worker_rlimit_nofile 200000;         # повышаем лимит открытых файлов для worker'ов (необходимо проверять с ulimit -n и /proc/sys/fs/file-max)
pid /run/nginx.pid;
error_log /var/log/nginx/error.log warn;

worker_cpu_affinity auto;                # привязка к CPU (если много ядер, полезно)

events {
    worker_connections 4096;         # макс соединений на процесс (пример)
    multi_accept on;                 # принимает все доступные соединения, когда приходит уведомление ядра
    use epoll;                       # эффективный метод обработки подключений
}

http {
    sendfile on; # копирование средствами ядра без обмена с пользователем
    tcp_nopush on; # Отправка заголовков одном пакетом
    tcp_nodelay on; # Отключение буферизации для keep-alive
    types_hash_max_size 2048;
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    
    keepalive_timeout 15s;  (15-30)         # время держать keepalive соединение
	keepalive_requests 1000;
	reset_timedout_connection on; # разрешить серверу закрывать соединения с безответными соединениями

    # лимиты
    limit_req_zone $binary_remote_addr zone=req_per_ip:10m rate=5r/s;
    limit_conn_zone $binary_remote_addr zone=conn_per_ip:10m;

    # кэширпование статики
    proxy_cache_path /var/cache/nginx/proxy_cache levels=1:2 keys_zone=my_cache:100m inactive=60m max_size=2g;
        
    open_file_cache max=20000 inactive=20s;
    open_file_cache_valid 30s;
    open_file_cache_min_uses 2;
    open_file_cache_errors on;

    # proxy buffers — уменьшают лишние syscalls и помогают при больших заголовках
    proxy_buffer_size 32k; # Не меньше самого большого htt[ response
    proxy_buffers 8 64k;

    # логирование понятное
    log_format pretty '$remote_addr -> $host "$request" $status $body_bytes_sent in $request_time sec ua="$http_user_agent"';
    access_log /var/log/nginx/access.log pretty;

    gzip on;                            # добавить сжатие (GZIP -> Brotli)
	gzip_min_length 10240;
	gzip_proxied expired no-cache no-store private auth;
	gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml;
    gzip_disable "msie6";


	# запрет небезопасных/ненужных методов
    map $request_method $allowed_method {
        default 0;
        GET 1;
        HEAD 1;
        POST 1;   # если нужен API/формы
        PUT 0;
        DELETE 0;
        OPTIONS 0;
        PATCH 0;
    }

    server_tokens off;                    # не показывать версию nginx
    

	server {
	
		listen 80;
		server_name board;
		
	    # Обрубить методы
	    if ($allowed_method = 0) {
            return 444;                    # тихо закрыть соединение
        }
        
        # Блокировка по ua
		if ($http_user_agent ~*(bingbot|AhrefsBot|PetalBot|SemrushBot|MJ12bot))
		{               
			return 403;       
		}
		
		# блокировка по гео
        if ($allowed_country = no) {          
            return 403;      
        }
        
        # Защита от долгих соединений
	    proxy_connect_timeout 15s;
	    proxy_send_timeout 15s;
	    proxy_read_timeout 15s;
	    
	    # статические файлы — отдавать из nginx (уменьшает нагрузку на бэкенд)
        location /static/ {
            root /var/www/myapp;
            expires 1h;
            add_header X-Content-Type-Options nosniff;
            try_files $uri =404;
        }
        
        location / {
	
			# минимальный rate limiting на location уровне
	        limit_req zone=req_per_ip burst=5 nodelay;
	        limit_conn conn_per_ip 10;
			
	        ...
	        proxy_pass http://backend_upstream;
	        ....
	        
	        
	        # блокировка IP
			deny 192.168.32.0/24;
	        allow 192.168.35.0/24;
        }
        
        # Блокировка файлов и дирректорий
		location /logs.txt {
	        deny all;
	    }
	    
		location /wp-admin {
	        deny all;
	    }
	}
	
	# балансировщик
	upstream myapp1 {  
       server srv1.example.com max_fails=3 fail_timeout=10s;  
       server srv2.example.com max_fails=3 fail_timeout=10s;  
       server srv3.example.com max_fails=3 fail_timeout=10s;  
       keepalive 32;
   }

    include /etc/nginx/conf.d/*.conf;
    include /etc/nginx/sites-enabled/*;
}

```

## Установка

```shell
apt install curl gnupg2 ca-certificates lsb-release debian-archive-keyring
```

```shell
curl https://nginx.org/keys/nginx_signing.key | gpg --dearmor \    | tee /usr/share/keyrings/nginx-archive-keyring.gpg >/dev/null
```

```shell
gpg --dry-run --quiet --import --import-options import-show /usr/share/keyrings/nginx-archive-keyring.gpg
```

```shell
echo "deb [signed-by=/usr/share/keyrings/nginx-archive-keyring.gpg] \http://nginx.org/packages/debian `lsb_release -cs` nginx" \    | tee /etc/apt/sources.list.d/nginx.list
```

```shell
echo -e "Package: *\nPin: origin nginx.org\nPin: release o=nginx\nPin-Priority: 900\n" \    | tee /etc/apt/preferences.d/99nginx
```

```shell
apt update
apt install -y nginx
```

```shell
nano /etc/hosts

{IP} {server_name}
```

## DoS test

**GoldenEye**
```shell
git clone https://github.com/jseidl/GoldenEye.git
cd ./GoldenEye

python3 goldeneye.py http://{domain}/test.png -w 50 -s 1500 -m random -d
```

**Oha**
```shell
git clone https://github.com/hatoo/oha
cd oha

<запуск>
```