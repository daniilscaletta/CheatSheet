#ddos 

> Действия, если сайт атакуют прямо сейчас

### Мониторинг через терминал

```bash
# Количество активных соединений
ss -an | grep :80 | wc -l
# Если больше 500 - возможна атака

# TOP IP-адресов по количеству соединений
netstat -an | grep :80 | awk '{print $5}' | cut -d: -f1 | sort | uniq -c | sort -rn | head -20

# Анализ логов Nginx на подозрительную активность
tail -f /var/log/nginx/access.log | grep -E "([0-9]{1,3}\.){3}[0-9]{1,3}" | awk '{print $1}' | sort | uniq -c | sort -rn

# Проверка загрузки сети
iftop -n
	```

## 1) Подтверждаем атаку

```bash
# Быстрая проверка нагрузки
uptime  # Load average не должен быть выше количества ядер CPU
df -h   # Проверка места на диске
free -m # Проверка памяти
```

## 2) Включаем базовую защиту

```bash
# Экстренная блокировка топ атакующих IP
netstat -an | grep :80 | awk '{print $5}' | cut -d: -f1 | sort | uniq -c | sort -rn | head -10 | while read count ip; do
  if [ $count -gt 50 ]; then
    iptables -A INPUT -s $ip -j DROP
    echo "Blocked $ip with $count connections"
  fi
done
# Включение SYN cookies
echo 1 > /proc/sys/net/ipv4/tcp_syncookies
# Ограничение новых соединений
iptables -A INPUT -p tcp --dport 80 -m recent --name http --update --seconds 1 --hitcount 10 -j DROP
```

## 3) Настройка Claudflare

Поставить галочку на `Under Attack Mode`

