#recon #osint #pentest #corporate #subdomain #dns #asn

> Первая фаза корпоративного пентеста — сбор информации о цели исключительно по домену, без активного взаимодействия с инфраструктурой

## Цель фазы

Максимально расширить **attack surface** до начала сканирования:
- Найти все точки входа (субдомены, IP-блоки, веб-приложения)
- Понять технологический стек
- Выявить утечки credentials и sensitive-данных
- Подготовить структурированный input для следующих фаз

---

## Структура выходных файлов

```
recon/
├── subs_raw.txt        # все найденные субдомены (сырые)
├── subs_resolved.txt   # субдомены с IP-адресами
├── live_web.txt        # живые веб-серверы (URL + статус + технологии)
├── ip_ranges.txt       # IP-диапазоны компании
├── emails.txt          # найденные email-адреса
└── findings/
    └── nuclei.txt      # результаты автосканера
```

```bash
mkdir -p recon/findings
```

---

## 1. DNS — базовая инфраструктура

> **Что делаем:** читаем DNS-записи домена. Раскрывает почтовую инфраструктуру, защиту от спуфинга, NS-провайдера, иногда всю зону

```bash
# Базовые записи
dig example.com ANY +noall +answer
dig example.com MX
dig example.com TXT      # SPF, DMARC, DKIM, верификации
dig example.com NS
dig example.com SOA

# Zone transfer — критично если сработает, отдаёт всю зону
dig axfr example.com @ns1.example.com
```

**На что смотреть:**

| Запись | Что ищем |
|--------|----------|
| `TXT` | SPF/DMARC — слабые настройки → фишинг от имени домена |
| `MX` | Почтовый провайдер (Office 365, Google, собственный) |
| `NS` | Регистратор и DNS-провайдер |
| `AXFR` | Если не запрещён — полная карта инфраструктуры |

**Веб-ресурсы:**

| Ресурс | Полезность | Для чего |
|--------|-----------|---------|
| [dnsdumpster.com](https://dnsdumpster.com) | ⭐⭐⭐⭐⭐ | Граф DNS + хосты + визуализация |
| [securitytrails.com](https://securitytrails.com) | ⭐⭐⭐⭐⭐ | Исторические DNS-записи |
| [viewdns.info](https://viewdns.info) | ⭐⭐⭐⭐ | Whois, reverse NS, история IP |
| [mxtoolbox.com](https://mxtoolbox.com) | ⭐⭐⭐ | Проверка MX, SPF, DMARC |

---

## 2. Субдомены

> **Что делаем:** собираем все субдомены через пассивные источники (CT-логи, поисковики, базы) и активный bruteforce DNS. Каждый субдомен — потенциально отдельное приложение со своей поверхностью атаки

### Пассивный сбор (без пакетов на цель)

```bash
# subfinder — агрегирует 50+ источников
subfinder -d example.com -all -recursive -o recon/subs_raw.txt

# amass — самый глубокий пассивный сбор, граф связей, больше источников
amass enum -passive -d example.com -o recon/amass_passive.txt
cat recon/amass_passive.txt >> recon/subs_raw.txt

# assetfinder — быстрый, хорош как дополнение
assetfinder --subs-only example.com >> recon/subs_raw.txt

# theHarvester — emails + субдомены через поисковики
theHarvester -d example.com -b google,bing,baidu -f recon/harvester_out

# CT-логи напрямую
curl -s "https://crt.sh/?q=%.example.com&output=json" \
  | jq -r '.[].name_value' | sed 's/\*\.//g' >> recon/subs_raw.txt
```

### Активный bruteforce DNS

```bash
# amass активный — bruteforce + scraping + permutations в одном
amass enum -active -brute -d example.com \
  -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt \
  -o recon/amass_active.txt
cat recon/amass_active.txt >> recon/subs_raw.txt

# puredns — быстрее, умеет wildcard-фильтрацию
puredns bruteforce /usr/share/seclists/Discovery/DNS/subdomains-top1million-20000.txt \
  example.com -r resolvers.txt -w recon/bruteforce_subs.txt

# gobuster DNS — классический
gobuster dns -d example.com \
  -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt \
  -o recon/gobuster_dns.txt

# ffuf — DNS mode + VHOST fuzzing (ловит виртуальные хосты не в DNS)
ffuf -u http://FUZZ.example.com \
  -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt \
  -mc 200,301,302,403 -o recon/ffuf_dns.json

# VHOST fuzzing — хосты за одним IP
ffuf -u https://example.com \
  -H "Host: FUZZ.example.com" \
  -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt \
  -mc 200,301,302,403 -fs 0 -o recon/ffuf_vhost.json
```

### Permutations (расширение найденного)

```bash
# dnsgen — генерирует вариации из уже найденных субдоменов
cat recon/subs_raw.txt | dnsgen - >> recon/subs_raw.txt

# gotator — permutations с кастомным словарём
gotator -sub recon/subs_raw.txt -perm permutations_small.txt -depth 1 \
  | sort -u >> recon/subs_raw.txt
```

### Резолвинг и дедупликация

```bash
# dnsx — массовый резолвинг, убирает несуществующие
cat recon/subs_raw.txt | sort -u | dnsx -silent -a -resp -o recon/subs_resolved.txt

# Только IP из resolved
cat recon/subs_resolved.txt | grep -oP '\d+\.\d+\.\d+\.\d+' | sort -u > recon/ips_from_dns.txt
```

### Subdomain Takeover

```bash
# subzy — проверяет все известные fingerprints
subzy run --targets recon/subs_resolved.txt --output recon/findings/takeovers.txt

# nuclei takeovers
nuclei -l recon/subs_resolved.txt -t takeovers/ -o recon/findings/nuclei_takeovers.txt
```

**Веб-ресурсы:**

| Ресурс | Полезность | Для чего |
|--------|-----------|---------|
| [crt.sh](https://crt.sh) | ⭐⭐⭐⭐⭐ | CT-логи сертификатов |
| [securitytrails.com](https://securitytrails.com) | ⭐⭐⭐⭐⭐ | Исторические субдомены |
| [shodan.io](https://shodan.io) | ⭐⭐⭐⭐⭐ | `ssl.cert.subject.cn:example.com` |
| [virustotal.com](https://virustotal.com) | ⭐⭐⭐⭐ | Relations tab по домену |
| [rapiddns.io](https://rapiddns.io) | ⭐⭐⭐ | Быстрый DNS lookup |
| [censys.io](https://censys.io) | ⭐⭐⭐ | Certificates search |

**Инструменты по полезности:**

| Инструмент  | Полезность | Установка                                                                                   |
| ----------- | ---------- | ------------------------------------------------------------------------------------------- |
| amass       | ⭐⭐⭐⭐⭐      | `go install github.com/owasp-amass/amass/v4/...@master`                                     |
| subfinder   | ⭐⭐⭐⭐⭐      | `go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest`                  |
| dnsx        | ⭐⭐⭐⭐⭐      | `go install github.com/projectdiscovery/dnsx/cmd/dnsx@latest`                               |
| ffuf        | ⭐⭐⭐⭐⭐      | `go install github.com/ffuf/ffuf/v2@latest`                                                 |
| puredns     | ⭐⭐⭐⭐       | `go install github.com/d3mondev/puredns/v2@latest`                                          |
| assetfinder | ⭐⭐⭐⭐       | `go install github.com/tomnomnom/assetfinder@latest`                                        |
| subzy       | ⭐⭐⭐        | `go install github.com/lc/subzy@latest`                                                     |
| dnsgen      | ⭐⭐⭐        | `pip3 install dnsgen`                                                                       |


---

## 3. ASN и IP-диапазоны

> **Что делаем:** находим весь IP-пул компании, включая серверы без DNS-имён — orphan hosts, старые стейджинги, забытые сервисы без WAF

```bash
# Найти ASN по домену/названию компании
curl -s "https://api.bgpview.io/search?query_term=Company+Name" \
  | jq '.data.asns[] | {asn, name, description}'

# asnmap — автоматически домен → ASN → IP-диапазоны
asnmap -d example.com -o recon/ip_ranges.txt

# Ручной способ: ASN → все его префиксы
whois -h whois.radb.net -- '-i origin AS12345' \
  | grep ^route \
  | awk '{print $2}' >> recon/ip_ranges.txt
```

**Важно:** диапазоны принадлежат ASN провайдера, не обязательно цели. Проверять каждый блок:

```bash
# Верифицировать принадлежность конкретного блока
whois 1.2.3.4 | grep -E "netname|org|descr" | head -5
```

**Веб-ресурсы:**

| Ресурс | Полезность | Для чего |
|--------|-----------|---------|
| [bgpview.io](https://bgpview.io) | ⭐⭐⭐⭐⭐ | ASN → IP-блоки, пиринг |
| [bgp.he.net](https://bgp.he.net) | ⭐⭐⭐⭐ | ASN lookup, граф |
| [shodan.io](https://shodan.io) | ⭐⭐⭐⭐⭐ | `org:"Company Name"` — все хосты |
| [ipinfo.io](https://ipinfo.io) | ⭐⭐⭐ | IP → org → ASN |

---

## 4. Живые веб-хосты

> **Что делаем:** из списка субдоменов и IP-диапазонов выявляем живые веб-серверы, получаем заголовки, технологии, статус-коды — визуальная карта attack surface

```bash
# httpx — основной инструмент, всё в одном
cat recon/subs_resolved.txt | httpx \
  -title -tech-detect -status-code \
  -follow-redirects -content-length \
  -o recon/live_web.txt

# Скриншоты для ручного просмотра
gowitness file -f recon/subs_resolved.txt -P recon/screenshots/
```

**Инструменты:**

| Инструмент | Полезность | Установка                                                       |
| ---------- | ---------- | --------------------------------------------------------------- |
| httpx      | ⭐⭐⭐⭐⭐      | `go install github.com/projectdiscovery/httpx/cmd/httpx@latest` |
| gowitness  | ⭐⭐⭐⭐       | `go install github.com/sensepost/gowitness@latest`              |


---

## 5. Утечки и credentials

> **Что делаем:** ищем пароли, API-ключи, internal URLs в публичных источниках — без единого пакета на цель, но с потенциально критическим результатом

### GitHub дорки

```
site:github.com "example.com" password
site:github.com "example.com" secret
site:github.com "example.com" api_key
site:github.com "@example.com"
site:github.com "example.com" internal
```

```bash
# trufflehog — сканирует GitHub org на secrets
trufflehog github --org=company-github-org --only-verified

# gitleaks — на конкретное репо
gitleaks detect --source ./cloned-repo
```

### Google дорки

```
site:example.com ext:env | ext:log | ext:sql | ext:bak | ext:conf
site:example.com intitle:"index of"
site:example.com "password" | "secret" | "api_key"
"example.com" site:pastebin.com
site:s3.amazonaws.com "example"
```

### Базы утечек

```bash
# dehashed API (платный, самый полный)
curl -s -u "email:api_key" \
  "https://api.dehashed.com/search?query=domain%3Aexample.com&size=100" \
  | jq '.entries[] | {email, password, hashed_password}'
```

**Веб-ресурсы:**

| Ресурс | Полезность | Для чего |
|--------|-----------|---------|
| [dehashed.com](https://dehashed.com) | ⭐⭐⭐⭐⭐ | `domain:example.com` — leaked creds |
| [intelx.io](https://intelx.io) | ⭐⭐⭐⭐⭐ | Агрегатор утечек, pastes |
| [grep.app](https://grep.app) | ⭐⭐⭐⭐ | Поиск по публичным git-репо |
| [leakix.net](https://leakix.net) | ⭐⭐⭐⭐ | Exposed services + утечки |
| [haveibeenpwned.com](https://haveibeenpwned.com) | ⭐⭐⭐ | Домен → количество утечек |

---

## 6. Люди и email-структура

> **Что делаем:** выясняем формат email-адресов, находим сотрудников — для password spray на VPN/OWA/O365 и понимания org-структуры

```bash
# theHarvester — emails через поисковики
theHarvester -d example.com -b google,linkedin,bing -o recon/emails.txt

# hunter.io API — формат + список сотрудников
curl "https://api.hunter.io/v2/domain-search?domain=example.com&api_key=KEY" \
  | jq '.data | {pattern: .pattern, emails: [.emails[].value]}' \
  >> recon/emails.txt
```

**Веб-ресурсы:**

| Ресурс | Полезность | Для чего |
|--------|-----------|---------|
| [hunter.io](https://hunter.io) | ⭐⭐⭐⭐⭐ | Email format + сотрудники |
| [linkedin.com](https://linkedin.com) | ⭐⭐⭐⭐ | `site:linkedin.com/in/ "example.com"` |
| [rocketreach.co](https://rocketreach.co) | ⭐⭐⭐ | Email lookup |
| [clearbit.com](https://clearbit.com) | ⭐⭐⭐ | Company + people data |

---

## 7. Технологии и версии

> **Что делаем:** fingerprint стека на живых хостах — находим устаревшие версии, уязвимые компоненты, CMS для целевых атак

```bash
# whatweb — детектирует технологии
whatweb https://example.com -a 3

# nuclei tech detect + CVE одновременно
nuclei -l recon/live_web.txt \
  -t technologies/ -t exposures/ -t cves/ \
  -o recon/findings/nuclei.txt

# Заголовки вручную
curl -sI https://example.com | grep -E "Server|X-Powered|X-Generator|X-AspNet"

# Favicon hash → Shodan поиск (найти копии/кластеры)
curl -s https://example.com/favicon.ico \
  | python3 -c "import sys,hashlib,base64; d=sys.stdin.buffer.read(); print(hashlib.md5(base64.encodebytes(d)).hexdigest())"
# → Shodan: http.favicon.hash:HASH
```

**Веб-ресурсы:**

| Ресурс | Полезность | Для чего |
|--------|-----------|---------|
| [shodan.io](https://shodan.io) | ⭐⭐⭐⭐⭐ | Favicon hash, banner, версии |
| [builtwith.com](https://builtwith.com) | ⭐⭐⭐⭐ | Полный tech stack |
| [wappalyzer.com](https://wappalyzer.com) | ⭐⭐⭐⭐ | Tech fingerprint |
| [vulners.com](https://vulners.com) | ⭐⭐⭐⭐ | CPE → CVE поиск |

---

## 8. OSINT-фреймворки (автоматизация всего сбора)

> **Что делаем:** запускаем агрегатор, который автоматически проходит DNS, субдомены, email, соцсети, утечки, shodan и сводит всё в граф или отчёт — хорошо для первичного быстрого охвата

### SpiderFoot

```bash
# Web UI (рекомендуется)
spiderfoot -l 127.0.0.1:5001

# CLI — сканирование домена по всем модулям
spiderfoot -s example.com -t INTERNET_NAME -m all -o recon/spiderfoot.csv

# Только пассивные модули (без активного взаимодействия с целью)
spiderfoot -s example.com -t INTERNET_NAME \
  -m sfp_dns,sfp_crt,sfp_shodan,sfp_haveibeenpwned,sfp_hunter \
  -o recon/spiderfoot_passive.csv
```

### Recon-ng

```bash
# Модульный фреймворк — как Metasploit для OSINT
recon-ng

# Внутри консоли:
marketplace install all
workspaces create example_com
modules load recon/domains-hosts/hackertarget
options set SOURCE example.com
run
```

### Maltego

Граф-визуализация связей — IP, домены, email, люди, организации. GUI-инструмент.
Лучший для презентации attack surface клиенту.

**Сравнение фреймворков:**

| Инструмент | Полезность | Тип | Установка |
|-----------|-----------|-----|---------|
| SpiderFoot | ⭐⭐⭐⭐⭐ | CLI + Web UI | `pip3 install spiderfoot` |
| Recon-ng | ⭐⭐⭐⭐ | CLI модульный | `pip3 install recon-ng` |
| Maltego CE | ⭐⭐⭐⭐ | GUI граф | maltego.com (free community) |
| theHarvester | ⭐⭐⭐⭐ | CLI | `pip3 install theHarvester` |

---

## Полный pipeline (от домена до карты)

```bash
TARGET="example.com"
mkdir -p recon/findings recon/screenshots

# 1. Субдомены (пассивный)
subfinder -d $TARGET -all -silent | tee recon/subs_raw.txt
amass enum -passive -d $TARGET -o recon/amass_passive.txt
cat recon/amass_passive.txt >> recon/subs_raw.txt
assetfinder --subs-only $TARGET >> recon/subs_raw.txt
curl -s "https://crt.sh/?q=%.${TARGET}&output=json" \
  | jq -r '.[].name_value' | sed 's/\*\.//g' >> recon/subs_raw.txt
cat recon/subs_raw.txt | sort -u | sponge recon/subs_raw.txt

# 1b. Субдомены (активный bruteforce + VHOST)
amass enum -active -brute -d $TARGET \
  -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt \
  >> recon/subs_raw.txt
ffuf -u http://FUZZ.$TARGET \
  -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt \
  -mc 200,301,302,403 -o recon/ffuf_dns.json -of json 2>/dev/null
cat recon/ffuf_dns.json | jq -r '.results[].input.FUZZ' 2>/dev/null \
  | sed "s/$/.${TARGET}/" >> recon/subs_raw.txt
cat recon/subs_raw.txt | sort -u | sponge recon/subs_raw.txt

# 2. Резолвинг
cat recon/subs_raw.txt | dnsx -silent -a -resp -o recon/subs_resolved.txt

# 3. Живые хосты
cat recon/subs_resolved.txt | httpx -silent -title -tech-detect \
  -status-code -o recon/live_web.txt

# 4. Скриншоты
gowitness file -f recon/subs_resolved.txt -P recon/screenshots/

# 5. Автосканирование
nuclei -l recon/live_web.txt \
  -t cves/ -t exposures/ -t takeovers/ -t misconfigurations/ \
  -o recon/findings/nuclei.txt

echo "[+] Субдоменов: $(wc -l < recon/subs_raw.txt)"
echo "[+] Живых хостов: $(wc -l < recon/live_web.txt)"
echo "[+] Findings: $(wc -l < recon/findings/nuclei.txt)"
```

---

## Следующая фаза

→ [[02 — Scanning & Enumeration]]
