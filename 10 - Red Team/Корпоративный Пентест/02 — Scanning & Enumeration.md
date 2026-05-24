#scanning #enumeration #pentest #nmap #corporate

> Фаза детального исследования каждого живого хоста и сервиса: точные версии, открытые порты, запущенные сервисы, пользователи, шары, конфиги — всё, что нужно для последующего анализа уязвимостей.

---

## Цель фазы

После [[01 — Recon]] у нас есть список IP-адресов, доменов и потенциально живых хостов. Задача Scanning & Enumeration — **углубиться в каждый хост**: узнать, что именно там запущено, какой версии, как сконфигурировано, и собрать данные об инфраструктуре (пользователи, группы, шары AD).

Все результаты сохраняются в папку `recon/` с чёткой структурой.

---

## 1. Port Scanning

### Инструменты

| Инструмент | Полезность | Install command |
|---|---|---|
| nmap | ⭐⭐⭐⭐⭐ | `sudo apt install nmap` / `brew install nmap` |
| masscan | ⭐⭐⭐⭐⭐ | `sudo apt install masscan` / `brew install masscan` |
| rustscan | ⭐⭐⭐⭐ | `cargo install rustscan` / `docker pull rustscan/rustscan` |
| naabu | ⭐⭐⭐⭐ | `go install github.com/projectdiscovery/naabu/v2/cmd/naabu@latest` |

### masscan — быстрый пре-скан

masscan используется первым: он находит открытые порты со скоростью миллионов пакетов в секунду. Результат передаётся в nmap для детального сканирования.

```bash
# Быстрый скан всех 65535 портов
sudo masscan -p1-65535 10.10.10.0/24 --rate=5000 -oG recon/ports/masscan.txt

# Извлечь только открытые порты
grep "open" recon/ports/masscan.txt | awk '{print $4}' | cut -d'/' -f1 | sort -u | tr '\n' ',' > recon/ports/ports.txt
```

### rustscan — ещё быстрее, с пайпом в nmap

```bash
# Скан с передачей результатов в nmap
rustscan -a 10.10.10.10 --ulimit 5000 -- -sV -sC -oA recon/nmap/host

# Скан подсети
rustscan -a 10.10.10.0/24 --ulimit 5000 -b 500 -- -sV -sC -oA recon/nmap/subnet
```

### nmap — основной инструмент детального сканирования

**Ключевые флаги:**

| Флаг | Описание |
|---|---|
| `-sV` | Service/version detection — определяет версию сервиса на каждом порту |
| `-sC` | Запускает дефолтные NSE-скрипты (эквивалент `--script=default`) |
| `-A` | Агрессивный режим: `-sV -sC -O --traceroute` |
| `-p-` | Сканировать все 65535 портов (вместо дефолтных топ-1000) |
| `--min-rate` | Минимальная скорость пакетов (например, `--min-rate 1000`) |
| `-Pn` | Не пинговать хост перед сканом (если хост блокирует ICMP) |
| `-oA` | Сохранить результаты в трёх форматах: `.xml`, `.nmap`, `.gnmap` |
| `-T4` | Временной шаблон (0-5): T4 — быстро, T3 — дефолт, T2 — тихо |

**Полный сценарий сканирования:**

```bash
# Шаг 1: Быстрый скан топ-портов для обнаружения хостов
nmap -sn 10.10.10.0/24 -oG recon/ports/alive_hosts.txt

# Шаг 2: Полный скан всех портов на конкретном хосте (быстро, без детектирования версий)
nmap -p- --min-rate 1000 -Pn 10.10.10.10 -oG recon/ports/full_ports.txt

# Шаг 3: Детальный скан только открытых портов
PORTS=$(grep "open" recon/ports/full_ports.txt | grep -oP '\d+/open' | cut -d'/' -f1 | tr '\n' ',')
nmap -sV -sC -p $PORTS -Pn 10.10.10.10 -oA recon/nmap/host

# Результаты: recon/nmap/host.xml, recon/nmap/host.nmap, recon/nmap/host.gnmap

# Агрессивный скан (шумно, но максимум инфо)
nmap -A -p- --min-rate 2000 -Pn 10.10.10.10 -oA recon/nmap/host_aggressive
```

### NSE-скрипты для распространённых сервисов

```bash
# SMB — базовые скрипты безопасности
nmap -p 445 --script smb-vuln*,smb-enum-shares,smb-enum-users 10.10.10.10

# HTTP/HTTPS — заголовки, методы, дефолтные крeды
nmap -p 80,443,8080 --script http-headers,http-methods,http-auth-finder,http-title 10.10.10.10

# FTP — анонимный вход
nmap -p 21 --script ftp-anon,ftp-syst,ftp-bounce 10.10.10.10

# SSH — алгоритмы шифрования
nmap -p 22 --script ssh2-enum-algos,ssh-auth-methods 10.10.10.10

# LDAP — null bind, базовая информация
nmap -p 389,636 --script ldap-rootdse,ldap-search 10.10.10.10

# SNMP
nmap -sU -p 161 --script snmp-info,snmp-sysdescr,snmp-interfaces 10.10.10.10

# RDP
nmap -p 3389 --script rdp-enum-encryption,rdp-vuln-ms12-020 10.10.10.10

# MSSQL
nmap -p 1433 --script ms-sql-info,ms-sql-empty-password,ms-sql-config 10.10.10.10

# MySQL
nmap -p 3306 --script mysql-info,mysql-empty-password,mysql-enum 10.10.10.10
```

### naabu — для web-ориентированных скопов

```bash
# Скан с фокусом на веб-портах
naabu -host 10.10.10.10 -p 80,443,8080,8443,3000,8000,4443,9090 -o recon/ports/naabu_web.txt

# Скан целого диапазона + интеграция с httpx
naabu -list targets.txt -p - -o recon/ports/naabu_all.txt | httpx -o recon/web/live_web.txt
```

---

## 2. Web Enumeration

### Инструменты

| Инструмент | Полезность | Install command |
|---|---|
| feroxbuster | ⭐⭐⭐⭐⭐ | `cargo install feroxbuster` / `apt install feroxbuster` |
| gobuster | ⭐⭐⭐⭐⭐ | `go install github.com/OJ/gobuster/v3@latest` |
| ffuf | ⭐⭐⭐⭐⭐ | `go install github.com/ffuf/ffuf/v2@latest` |
| dirsearch | ⭐⭐⭐⭐ | `pip3 install dirsearch` |
| httpx | ⭐⭐⭐⭐⭐ | `go install github.com/projectdiscovery/httpx/cmd/httpx@latest` |
| whatweb | ⭐⭐⭐⭐ | `apt install whatweb` / `gem install whatweb` |
| nikto | ⭐⭐⭐ | `apt install nikto` |
| arjun | ⭐⭐⭐⭐ | `pip3 install arjun` |

### Подготовка — определение живых веб-сервисов

```bash
# Проверить все найденные порты на наличие HTTP/HTTPS
cat recon/ports/ports.txt | httpx -title -status-code -tech-detect -o recon/web/live_web.txt

# Получить технологии и заголовки
whatweb http://10.10.10.10 -a 3 --log-verbose recon/web/whatweb.txt
```

### Bruteforce директорий и файлов

**feroxbuster** — рекурсивный, быстрый, с поддержкой фильтрации:

```bash
# Базовый рекурсивный брутфорс
feroxbuster -u http://10.10.10.10 \
  -w /usr/share/seclists/Discovery/Web-Content/directory-list-2.3-medium.txt \
  -x php,html,txt,bak,old,zip,tar,gz,conf,config,json,xml \
  -o recon/web/ferox_dirs.txt \
  --threads 50 \
  --depth 3

# С фильтрацией 404/403
feroxbuster -u http://10.10.10.10 \
  -w /usr/share/seclists/Discovery/Web-Content/raft-large-directories.txt \
  --filter-status 404,403 \
  -o recon/web/ferox_dirs_filtered.txt
```

**gobuster** — стабильный, хорошо работает с vhosts и DNS:

```bash
# Директории
gobuster dir \
  -u http://10.10.10.10 \
  -w /usr/share/seclists/Discovery/Web-Content/directory-list-2.3-medium.txt \
  -x php,aspx,html,txt,bak,zip \
  -o recon/web/gobuster_dirs.txt \
  -t 50

# Virtual hosts (subdomain bruteforce)
gobuster vhost \
  -u http://target.local \
  -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-20000.txt \
  --append-domain \
  -o recon/web/gobuster_vhosts.txt
```

### API endpoint discovery

```bash
# Поиск API-эндпоинтов
gobuster dir \
  -u http://10.10.10.10 \
  -w /usr/share/seclists/Discovery/Web-Content/api/api-endpoints.txt \
  -o recon/web/gobuster_api.txt

# ffuf для API с JSON-ответами
ffuf -u http://10.10.10.10/api/FUZZ \
  -w /usr/share/seclists/Discovery/Web-Content/api/objects.txt \
  -mc 200,201,204,301,302,400,401,403 \
  -o recon/web/ffuf_api.json \
  -of json

# Поиск скрытых параметров с arjun
arjun -u http://10.10.10.10/api/users -m GET -o recon/web/arjun_params.json
```

### Поиск бэкапов и конфигов

```bash
# Backup и конфиг-файлы
ffuf -u http://10.10.10.10/FUZZ \
  -w /usr/share/seclists/Discovery/Web-Content/backup-files.txt \
  -mc 200 \
  -o recon/web/ffuf_backups.json

# Специфичные расширения бэкапов
ffuf -u http://10.10.10.10/FUZZ \
  -w /usr/share/seclists/Discovery/Web-Content/Common-DB-Backups.txt \
  -e .bak,.old,.orig,.backup,.sql,.tar.gz,.zip \
  -mc 200,301 \
  -o recon/web/ffuf_config_backup.json
```

### Parameter fuzzing

```bash
# GET-параметры
ffuf -u "http://10.10.10.10/page?FUZZ=test" \
  -w /usr/share/seclists/Discovery/Web-Content/burp-parameter-names.txt \
  -mc 200 \
  -fs 1234 \
  -o recon/web/ffuf_params_get.json

# POST-параметры
ffuf -u http://10.10.10.10/login \
  -w /usr/share/seclists/Discovery/Web-Content/burp-parameter-names.txt \
  -X POST \
  -d "FUZZ=test" \
  -mc 200,302 \
  -o recon/web/ffuf_params_post.json
```

### Полезные ресурсы

| Resource | Полезность | Purpose |
|---|---|---|
| SecLists (danielmiessler) | ⭐⭐⭐⭐⭐ | Главная коллекция wordlist'ов |
| FuzzDB | ⭐⭐⭐⭐ | Wordlists для fuzzing и атак |
| PayloadsAllTheThings | ⭐⭐⭐⭐⭐ | Payload'ы для всех типов уязвимостей |
| Assetnote Wordlists | ⭐⭐⭐⭐⭐ | Wordlists для API и технологий |

---

## 3. SMB Enumeration

### Инструменты

| Инструмент | Полезность | Install command |
|---|---|
| enum4linux-ng | ⭐⭐⭐⭐⭐ | `pip3 install enum4linux-ng` / `apt install enum4linux-ng` |
| crackmapexec | ⭐⭐⭐⭐⭐ | `pip3 install crackmapexec` / `apt install crackmapexec` |
| smbmap | ⭐⭐⭐⭐ | `pip3 install smbmap` / `apt install smbmap` |
| smbclient | ⭐⭐⭐⭐ | `apt install smbclient` |
| impacket | ⭐⭐⭐⭐⭐ | `pip3 install impacket` |

### enum4linux-ng — комплексная энумерация

```bash
# Полная энумерация (null session)
enum4linux-ng -A 10.10.10.10 -oJ recon/smb/enum4linux.json -oY recon/smb/enum4linux.yaml

# Конкретные задачи
enum4linux-ng -U 10.10.10.10   # только пользователи
enum4linux-ng -G 10.10.10.10   # только группы
enum4linux-ng -S 10.10.10.10   # только шары
enum4linux-ng -P 10.10.10.10   # парольная политика
```

### crackmapexec — швейцарский нож для SMB

```bash
# Базовая информация о хосте
crackmapexec smb 10.10.10.10

# Скан подсети
crackmapexec smb 10.10.10.0/24 --gen-relay-list recon/smb/relay_targets.txt

# Список шар (null session)
crackmapexec smb 10.10.10.10 -u '' -p '' --shares

# Список шар с кредами
crackmapexec smb 10.10.10.10 -u 'user' -p 'password' --shares

# Список пользователей
crackmapexec smb 10.10.10.10 -u '' -p '' --users 2>/dev/null | tee recon/smb/cme_users.txt

# RID брутфорс для получения пользователей
crackmapexec smb 10.10.10.10 -u '' -p '' --rid-brute | tee recon/smb/cme_rid.txt

# Информация о домене
crackmapexec smb 10.10.10.10 --pass-pol | tee recon/smb/cme_passpol.txt

# Выполнение команды (если есть права)
crackmapexec smb 10.10.10.10 -u 'admin' -p 'password' -x 'whoami'

# Дамп SAM (требует прав)
crackmapexec smb 10.10.10.10 -u 'admin' -p 'password' --sam
```

### smbmap — просмотр содержимого шар

```bash
# Список шар и прав (null session)
smbmap -H 10.10.10.10 | tee recon/smb/smbmap_shares.txt

# Рекурсивный листинг
smbmap -H 10.10.10.10 -r 'Share' | tee recon/smb/smbmap_listing.txt

# С кредами
smbmap -H 10.10.10.10 -u 'user' -p 'password' -r 'Share'

# Скачать файл
smbmap -H 10.10.10.10 -u 'user' -p 'password' --download 'Share/important.txt'
```

### smbclient — ручная работа с шарами

```bash
# Список шар (null session)
smbclient -L //10.10.10.10 -N | tee recon/smb/smbclient_shares.txt

# Подключиться к шаре
smbclient //10.10.10.10/Share -N
smbclient //10.10.10.10/Share -U 'user%password'

# Команды внутри smbclient:
# ls          — листинг
# get file    — скачать файл
# mget *      — скачать все файлы
# recurse ON  — рекурсивный режим
# prompt OFF  — без подтверждений
```

### Что искать при SMB-энумерации

- **Null session** — доступ без аутентификации
- **Открытые шары** с чувствительными данными (конфиги, пароли, бэкапы)
- **Список пользователей домена** — для password spraying
- **Парольная политика** — минимальная длина, lockout threshold
- **Информация о домене** — имя домена, DC, OS-версии
- **Signing disabled** — уязвимо к NTLM relay атакам

```bash
# Проверка подписи (signing)
crackmapexec smb 10.10.10.0/24 | grep -i "signing"
```

---

## 4. LDAP / Active Directory

### Инструменты

| Инструмент | Полезность | Install command |
|---|---|
| ldapdomaindump | ⭐⭐⭐⭐⭐ | `pip3 install ldapdomaindump` |
| crackmapexec ldap | ⭐⭐⭐⭐⭐ | (входит в crackmapexec) |
| ldapsearch | ⭐⭐⭐⭐ | `apt install ldap-utils` |
| bloodhound-python | ⭐⭐⭐⭐⭐ | `pip3 install bloodhound` |
| windapsearch | ⭐⭐⭐⭐ | `go install github.com/ropnop/windapsearch@latest` |

### ldapsearch — null bind и базовая информация

```bash
# Null bind — получить базовую информацию о домене
ldapsearch -x -H ldap://10.10.10.10 -b '' -s base '(objectClass=*)' \
  namingContexts defaultNamingContext | tee recon/ldap/ldap_base.txt

# Получить всех пользователей (null bind)
ldapsearch -x -H ldap://10.10.10.10 \
  -b 'DC=domain,DC=local' \
  '(objectClass=user)' sAMAccountName userPrincipalName memberOf \
  2>/dev/null | tee recon/ldap/ldap_users.txt

# С кредами — полный дамп
ldapsearch -x -H ldap://10.10.10.10 \
  -D 'user@domain.local' -w 'password' \
  -b 'DC=domain,DC=local' \
  '(objectClass=*)' | tee recon/ldap/ldap_full.txt

# Парольная политика
ldapsearch -x -H ldap://10.10.10.10 \
  -b 'DC=domain,DC=local' \
  '(objectClass=domainDNS)' pwdHistoryLength lockoutThreshold lockoutDuration
```

### ldapdomaindump — структурированный дамп AD

```bash
# Полный дамп с кредами (создаёт HTML + JSON файлы)
ldapdomaindump -u 'domain\user' -p 'password' \
  ldap://10.10.10.10 \
  -o recon/ldap/ldapdomaindump/

# Null bind (если доступен)
ldapdomaindump ldap://10.10.10.10 -o recon/ldap/ldapdomaindump/

# Результаты: domain_users.json, domain_groups.json, domain_computers.json, ...
```

### crackmapexec ldap

```bash
# Базовая информация о домене
crackmapexec ldap 10.10.10.10 -u '' -p ''

# Пользователи
crackmapexec ldap 10.10.10.10 -u 'user' -p 'password' --users | tee recon/ldap/cme_ldap_users.txt

# Группы
crackmapexec ldap 10.10.10.10 -u 'user' -p 'password' --groups | tee recon/ldap/cme_ldap_groups.txt

# Парольная политика
crackmapexec ldap 10.10.10.10 -u 'user' -p 'password' --pass-pol

# ASREPRoastable пользователи (без Kerberos pre-auth)
crackmapexec ldap 10.10.10.10 -u 'user' -p 'password' --asreproast recon/ldap/asreproast.txt

# Kerberoastable пользователи (SPN)
crackmapexec ldap 10.10.10.10 -u 'user' -p 'password' --kerberoasting recon/ldap/kerberoast.txt
```

### Что извлекать из LDAP/AD

- **Пользователи** — sAMAccountName, email, описания (часто содержат пароли!)
- **Группы** — членство, особенно Domain Admins, Enterprise Admins
- **Парольная политика** — для планирования spraying атак без lockout
- **Компьютеры домена** — список хостов, OS-версии
- **SPN** — сервисные аккаунты для Kerberoasting
- **Пользователи без pre-auth** — для AS-REP Roasting
- **AdminCount=1** — привилегированные аккаунты

---

## 5. Other Services

### SNMP

```bash
# onesixtyone — брутфорс community strings
onesixtyone -c /usr/share/seclists/Discovery/SNMP/snmp.txt 10.10.10.10 \
  | tee recon/services/snmp_communities.txt

# snmpwalk — получить всё дерево MIB
snmpwalk -v2c -c public 10.10.10.10 | tee recon/services/snmpwalk_full.txt

# Системная информация
snmpwalk -v2c -c public 10.10.10.10 1.3.6.1.2.1.1
# Запущенные процессы
snmpwalk -v2c -c public 10.10.10.10 1.3.6.1.2.1.25.4.2
# Установленное ПО
snmpwalk -v2c -c public 10.10.10.10 1.3.6.1.2.1.25.6.3
# Пользователи
snmpwalk -v2c -c public 10.10.10.10 1.3.6.1.4.1.77.1.2.25
```

### FTP

```bash
# Анонимный вход
ftp 10.10.10.10
# Логин: anonymous / Пароль: anonymous или пустой

# Через nmap
nmap -p 21 --script ftp-anon 10.10.10.10

# Если анонимный доступ открыт — скачать всё
wget -m --no-passive ftp://anonymous:anonymous@10.10.10.10 -P recon/services/ftp/
```

### SSH

```bash
# Баннер и версия
nc -nv 10.10.10.10 22

# Поддерживаемые алгоритмы
nmap -p 22 --script ssh2-enum-algos 10.10.10.10

# Методы аутентификации
nmap -p 22 --script ssh-auth-methods --script-args="ssh.user=root" 10.10.10.10
```

### RDP

```bash
# Проверка доступности
nmap -p 3389 --script rdp-enum-encryption 10.10.10.10

# Скриншот экрана входа (без крежов)
nmap -p 3389 --script rdp-screenshot 10.10.10.10

# crackmapexec
crackmapexec rdp 10.10.10.10
```

### Redis

```bash
# Подключение без пароля
redis-cli -h 10.10.10.10 ping
redis-cli -h 10.10.10.10 info server
redis-cli -h 10.10.10.10 keys '*'
```

### MongoDB

```bash
# Подключение без аутентификации
mongosh "mongodb://10.10.10.10:27017" --eval "db.adminCommand({listDatabases:1})"

# Через nmap
nmap -p 27017 --script mongodb-info 10.10.10.10
```

### Elasticsearch

```bash
# Проверка открытого доступа
curl -s http://10.10.10.10:9200/_cat/indices?v | tee recon/services/elastic_indices.txt
curl -s http://10.10.10.10:9200/_cluster/health | tee recon/services/elastic_health.txt

# Получить все документы из индекса
curl -s "http://10.10.10.10:9200/index_name/_search?size=100" | python3 -m json.tool
```

---

## 6. Full Pipeline

Автоматизированный скрипт, который последовательно выполняет весь цикл сканирования и сохраняет структурированные результаты.

```bash
#!/usr/bin/env bash
# scan_pipeline.sh — полный pipeline сканирования
# Использование: ./scan_pipeline.sh <target_ip> [subnet]

set -euo pipefail

TARGET="${1:?Укажите IP цели}"
SUBNET="${2:-$TARGET}"
OUTPUT_DIR="recon"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Цвета для вывода
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
log() { echo -e "${GREEN}[*]${NC} $1"; }
warn() { echo -e "${YELLOW}[!]${NC} $1"; }

# Создать структуру папок
mkdir -p "$OUTPUT_DIR"/{ports,nmap,web,smb,ldap,services,screenshots}
log "Структура папок создана: $OUTPUT_DIR/"

## ─── ЭТАП 1: Port Scanning ──────────────────────────────────────────────────

log "Этап 1: masscan — быстрый скан всех портов ($TARGET)"
sudo masscan -p1-65535 "$TARGET" --rate=3000 \
  -oG "$OUTPUT_DIR/ports/masscan_${TIMESTAMP}.txt" 2>/dev/null

# Извлечь открытые порты
OPEN_PORTS=$(grep "open" "$OUTPUT_DIR/ports/masscan_${TIMESTAMP}.txt" \
  | awk '{print $4}' | cut -d'/' -f1 | sort -un | tr '\n' ',' | sed 's/,$//')

if [[ -z "$OPEN_PORTS" ]]; then
  warn "masscan не нашёл открытых портов, пробуем nmap напрямую"
  OPEN_PORTS="1-65535"
fi

echo "$OPEN_PORTS" > "$OUTPUT_DIR/ports/ports.txt"
log "Открытые порты: $OPEN_PORTS"

## ─── ЭТАП 2: nmap детальное сканирование ────────────────────────────────────

log "Этап 2: nmap — детальный скан открытых портов"
nmap -sV -sC -p "$OPEN_PORTS" -Pn --min-rate 1000 \
  "$TARGET" \
  -oA "$OUTPUT_DIR/nmap/host" \
  --reason 2>/dev/null | tee "$OUTPUT_DIR/nmap/host_stdout.txt"

log "Результаты nmap: $OUTPUT_DIR/nmap/host.{xml,nmap,gnmap}"

## ─── ЭТАП 3: Service-specific enumeration ───────────────────────────────────

log "Этап 3: Энумерация сервисов по портам"

# SMB (445, 139)
if echo "$OPEN_PORTS" | grep -qE "445|139"; then
  log "  → SMB обнаружен, запускаем энумерацию"
  crackmapexec smb "$TARGET" \
    > "$OUTPUT_DIR/smb/cme_info.txt" 2>/dev/null || true
  enum4linux-ng -A "$TARGET" \
    -oJ "$OUTPUT_DIR/smb/enum4linux.json" 2>/dev/null || true
  smbmap -H "$TARGET" \
    > "$OUTPUT_DIR/smb/smbmap_shares.txt" 2>/dev/null || true
fi

# LDAP (389, 636)
if echo "$OPEN_PORTS" | grep -qE "389|636|3268|3269"; then
  log "  → LDAP обнаружен, запускаем энумерацию"
  ldapsearch -x -H "ldap://$TARGET" -b '' -s base '(objectClass=*)' \
    namingContexts 2>/dev/null \
    > "$OUTPUT_DIR/ldap/ldap_base.txt" || true
fi

# SNMP (161/udp)
log "  → Проверка SNMP"
onesixtyone -c /usr/share/seclists/Discovery/SNMP/snmp.txt "$TARGET" \
  > "$OUTPUT_DIR/services/snmp_communities.txt" 2>/dev/null || true

# FTP (21)
if echo "$OPEN_PORTS" | grep -q "21"; then
  log "  → FTP обнаружен, проверяем анонимный вход"
  nmap -p 21 --script ftp-anon "$TARGET" \
    > "$OUTPUT_DIR/services/ftp_anon.txt" 2>/dev/null || true
fi

## ─── ЭТАП 4: Web Enumeration ────────────────────────────────────────────────

WEB_PORTS=$(echo "$OPEN_PORTS" | tr ',' '\n' \
  | grep -E "^(80|443|8080|8443|8000|8888|3000|9090|4443)$" \
  | tr '\n' ',' | sed 's/,$//')

if [[ -n "$WEB_PORTS" ]]; then
  log "Этап 4: Web-энумерация на портах: $WEB_PORTS"

  for PORT in $(echo "$WEB_PORTS" | tr ',' ' '); do
    PROTO="http"
    [[ "$PORT" =~ ^(443|8443|4443)$ ]] && PROTO="https"
    URL="${PROTO}://${TARGET}:${PORT}"

    log "  → feroxbuster на $URL"
    feroxbuster -u "$URL" \
      -w /usr/share/seclists/Discovery/Web-Content/directory-list-2.3-medium.txt \
      -x php,html,txt,bak,zip,conf \
      -o "$OUTPUT_DIR/web/ferox_${PORT}.txt" \
      --threads 30 --depth 2 \
      --silent 2>/dev/null || true
  done
fi

## ─── ФИНАЛ ──────────────────────────────────────────────────────────────────

log "Pipeline завершён. Результаты в: $OUTPUT_DIR/"
find "$OUTPUT_DIR" -type f | sort
```

---

## 7. Структура выходных файлов

```
recon/
├── ports/
│   ├── masscan_20240101_120000.txt    # сырые результаты masscan
│   ├── ports.txt                      # только номера открытых портов (csv)
│   └── alive_hosts.txt               # живые хосты в сети
│
├── nmap/
│   ├── host.xml                       # nmap XML (для парсинга)
│   ├── host.nmap                      # nmap читаемый текст
│   ├── host.gnmap                     # nmap greppable формат
│   └── host_stdout.txt               # вывод в консоль
│
├── web/
│   ├── live_web.txt                   # список живых веб-сервисов (httpx)
│   ├── whatweb.txt                    # технологии и заголовки
│   ├── ferox_80.txt                   # feroxbuster порт 80
│   ├── ferox_443.txt                  # feroxbuster порт 443
│   ├── gobuster_dirs.txt             # gobuster директории
│   ├── gobuster_vhosts.txt           # gobuster virtual hosts
│   ├── ffuf_api.json                  # ffuf API-эндпоинты
│   ├── ffuf_backups.json             # ffuf бэкапы и конфиги
│   ├── ffuf_params_get.json          # ffuf GET-параметры
│   └── arjun_params.json             # arjun скрытые параметры
│
├── smb/
│   ├── cme_info.txt                   # crackmapexec базовая инфо
│   ├── cme_users.txt                  # список пользователей
│   ├── cme_rid.txt                    # RID brute результаты
│   ├── cme_passpol.txt               # парольная политика
│   ├── enum4linux.json               # enum4linux-ng JSON
│   ├── smbmap_shares.txt             # список шар и прав
│   ├── smbclient_shares.txt          # smbclient листинг
│   └── relay_targets.txt             # цели без SMB signing
│
├── ldap/
│   ├── ldap_base.txt                  # базовая информация домена
│   ├── ldap_users.txt                 # пользователи AD
│   ├── ldap_full.txt                  # полный LDAP дамп
│   ├── cme_ldap_users.txt            # crackmapexec пользователи
│   ├── cme_ldap_groups.txt           # crackmapexec группы
│   ├── asreproast.txt                 # AS-REP Roastable хеши
│   ├── kerberoast.txt                 # Kerberoastable хеши
│   └── ldapdomaindump/               # папка ldapdomaindump
│       ├── domain_users.json
│       ├── domain_groups.json
│       ├── domain_computers.json
│       └── domain_policy.json
│
└── services/
    ├── snmp_communities.txt           # SNMP community strings
    ├── snmpwalk_full.txt              # полное SNMP дерево
    ├── ftp_anon.txt                   # результат FTP anonymous check
    ├── elastic_indices.txt            # Elasticsearch индексы
    └── elastic_health.txt             # Elasticsearch health
```

---

→ [[03 — Vulnerability Analysis]]
