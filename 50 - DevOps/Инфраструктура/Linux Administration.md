#Linux 

## Capabilities

> Механизм, ограничивающий права root (Разбивает на 40+ прав)

### Основные права
#### **1. Файловая система:**
- `CAP_DAC_OVERRIDE` - игнорировать все права доступа к файлам
- `CAP_DAC_READ_SEARCH` - игнорировать права на чтение/поиск
- `CAP_CHOWN` - изменять владельца файлов
- `CAP_FOWNER` - игнорировать проверки владельца
#### **2. Сетевые:**
- `CAP_NET_RAW` - использовать RAW сокеты (ping, traceroute)
- `CAP_NET_BIND_SERVICE` - биндиться на порты < 1024
- `CAP_NET_ADMIN` - настройка сети (iptables, маршруты
#### **3. Системные:**
- `CAP_SYS_ADMIN` - "мини-root" (монтирование, администрирование)
- `CAP_SYS_MODULE` - загружать/выгружать модули ядра
- `CAP_SYS_PTRACE` - отлаживать процессы (ptrace)
- `CAP_SYS_TIME` - изменять системное время
#### **4. Процессы:**
- `CAP_KILL` - убивать любые процессы
- `CAP_SETUID` - изменять UID процесса
- `CAP_SYS_NICE` - изменять приоритет процессов

## Просмотр capabilities

```shell
# Какие capabilities у файла?

## Оглавление
- [[#Capabilities]]
  - [[#Основные права]]
- [[#Просмотр capabilities]]
- [[#Установка capabilities]]
- [[#Tools]]

---

getcap /usr/bin/ping
/usr/bin/ping = cap_net_raw+ep

# Все файлы с capabilities
getcap -r / 2>/dev/null
```


## Установка capabilities

```shell
sudo setcap cap_dac_read_search+ep <бинарь>
```

## Tools

1) CDK
```shell
./cdk audit # проверка всех capabilities
```

2) kube-hunter
```shell
kube-hunter # Сканирование Kubernetes на уязвимости
```

3) amicontained
```shell
amicontained # Анализ изоляции контейнера
```