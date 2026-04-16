#nginx #ddos 

## Анализ / Просмотр

Сопоставление IP и кол-во запросов
```bash
cat /var/log/nginx/access.log | awk '{print $1}'| sort -nr | uniq -c | sort -nr | head
```

Определить кол-во уникальных IP
```shell
cat /var/log/nginx/access.log | awk '{print $1}'| sort -nr | uniq -c | wc -l
```

Количество запросов на IP в данный час
```shell
cat /var/log/nginx/access.log | grep "25/Oct/2025:20:" | awk '{print $1}' | sort | uniq -c | sort -nr
```

Просмотр ошибок
```shell
cat /var/log/nginx/error.log
```

## Подключение WAF ModSecurity

1) Установка + установка правил
```bash
sudo apt install nginx nginx-modsecurity
sudo apt install modsecurity-crs
```

2) Включаем WAF, открываем `/etc/nginx/modsec/main.con`
```bash
SecRuleEngine On
```

3) Подключаем в nginx.conf (В http / server / location)
```bash
modsecurity on;
modsecurity_rules_file /etc/nginx/modsec/main.conf;
```

4) Добавляем правила (в main.conf)
```bash
Include /usr/share/modsecurity-crs/*.conf
Include /usr/share/modsecurity-crs/rules/*.conf
```

## Fail2ban

Анализирует логи и на основе правила блокирует IP

```shell
apt install fail2ban
```

```shell
cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
```

```shell
nano /etc/fail2ban/jail.local
```

В конец добавляем
```shell
[nginx-limit-req]
enabled = true
filter  = nginx-limit-req
port    = http,https
logpath = /var/log/nginx/*error.log
findetime = 600
bantime = 600
maxretry = 5
# ignoreip - ip, которые не должны быть заблочены

## Оглавление
- [[#Анализ / Просмотр]]
- [[#Подключение WAF ModSecurity]]
- [[#Fail2ban]]
- [[#geoIP]]
- [[#Защита от SYN-flood]]
- [[#Защита от TCP-connection exhaustion]]
- [[#Защита от HTTP flood]]
- [[#Metrics]]
- [[#Alerts]]

---


[http-get-dos]
enabled = true
port = http,https
filter = http-get-dos
logpath = /var/log/nginx/access.log
maxretry = 300
findtime = 300
bantime = 600
action = iptables[name=HTTP, port=http, protocol=tcp]
```

```shell
fail2ban-client reload

systemctl restart fail2ban

fail2ban-client status nginx-limit-req
```

## geoIP

Блокируем трафик из ненужных стран

```shell
add-apt-repository ppa:maxmind/ppa
apt update
apt install libmaxminddb0 libmaxminddb-dev mmdb-bin
```

Компилируем под нужную версию nginx
```shell
cd /rootwget http://nginx.org/download/nginx-1.18.0.tar.gz
git clone https://github.com/leev/ngx_http_geoip2_module.git
tar zxvf nginx-1.18.0.tar.gzcd nginx-1.18.0
./configure --with-compat --add-dynamic-module=../ngx_http_geoip2_module
make modules
```

```shell
mkdir -p /etc/nginx/modulescp -vi objs/ngx_http_geoip2_module.so /etc/nginx/modules/
```

Скачиваем БД с актуальными IP
```shell
mkdir /etc/nginx/geoip
cd /etc/nginx/geoip
wget https://git.io/GeoLite2-Country.mmdb
```

Далее вставляем в nginx.conf

```
load_module modules/ngx_http_geoip2_module.so;


...

http {         
	geoip2 /etc/nginx/geoip/GeoLite2-Country.mmdb {                                      $geoip2_data_country_iso_code country iso_code;                              }        
	
	map $geoip2_data_country_iso_code $is_deny {                                         default no; # Запрещаем всем           
	    RU yes; # Разрешаем России	    
	    UK yes; # Разрешаем Великобритании       
	}
}
```

```shell
nginx -s reload
```

## Защита от SYN-flood

SYN-flood
```shell
hping3 -S --flood --rand-source -p 80 1.2.3.4
```

Защита
```shell
echo 1 > /proc/sys/net/ipv4/tcp_syncookies # Включение SYN cookie
echo 4096 >  /proc/sys/net/ipv4/tcp_max_syn_backlog 
echo 2 > /proc/sys/net/ipv4/tcp_synack_retries 
```

## Защита от TCP-connection exhaustion

```shell
net.ipv4.tcp_syn_retries = 2
net.ipv4.tcp_tw_reuse = 1
``

1. Режем keepalive:
```shell
net.ipv4.tcp_keepalive_time = 60 # default: 7200 (2 hour)
net.ipv4.tcp_keepalive_probes = 6 # default: 9
net.ipv4.tcp_keepalive_intvl = 5 # default 75 second
```

2. Уменьшаем количество ретраев:
```shell
net.ipv4.tcp_synack_retries = 2 # default 5
net.ipv4.tcp_retries2 = 8 # default 15
net.ipv4.tcp_fin_timeout = 5 # default 60 seconds
```


## Защита от HTTP flood

Атака 
```shell
wrk -t96 -c10000 -d30s https://your.awesome.site/
```

Сервер сам проверяет корректность сертификата
```nginx
ssl_stapling on;

ssl_session_tickets on;
```

## Metrics

[angie  модуль](https://angie.software/)

[дашборд для графаны](https://grafana.com/grafana/dashboards/20719-angie-dashboard/)

## Alerts

![[Alerts for nginx.png]]