
# **СОДЕРЖАНИЕ**

[[#1. RECON]]
	[[#Passive RECON]]
	[[#Active RECON]]

# 1. RECON 

## Passive RECON

### 1.1. Сетевая инфраструктура (Infrastructure)

|Подэтап|Что собираем (Цель)|Инструменты|
|---|---|---|
|**ASN & IP Discovery**|Диапазоны IP-адресов, владельцы сетей, связанные организации.|BGP Toolkit (HE), RIPE, ARIN, IANA.|
|**DNS History**|Исторические IP-адреса (поиск реального IP за Cloudflare/WAF).|SecurityTrails, ViewDNS, DNSDumpster.|
|**Passive Subdomains**|Список всех когда-либо существовавших поддоменов из кэша.|**Subfinder**, **Amass (passive)**, **Crt.sh**, **Assetfinder**.|
|**Cloud Assets**|Забытые или открытые хранилища данных (S3 бакеты, Azure Blobs).|GrayHatWarfare, CloudEnum.|
### 1.2. Анализ документов и кода (Data Disclosure)

|Подэтап|Что собираем (Цель)|Инструменты|
|---|---|---|
|**Metadata Mining**|Логины сотрудников, внутренние пути (`C:\Users\...`), версии ПО, имена серверов.|**FOCA**, **Metagoofil**, **ExifTool**.|
|**GitHub/GitLab OSINT**|API-ключи, пароли, токены, внутренние конфиги, комментарии разработчиков.|**TruffleHog**, **Git-hound**, **Gitleaks**, GitHub Dorks.|
|**Google Dorking**|Списки файлов, панели входа, лог-файлы, проиндексированные конфиги.|Google, Exploit-DB (GHDB).|
### 1.3. Люди и учетные данные (Identity & Employees)

|Подэтап|Что собираем (Цель)|Инструменты|
|---|---|---|
|**Email Discovery**|Корпоративные адреса, структура именования почт (логины).|**Hunter.io**, **TheHarvester**, Phonebook.cz.|
|**Staff Profiling**|Имена сотрудников, должности, иерархия, используемые технологии (через вакансии).|LinkedIn, Indeed, Glassdoor, HH.ru.|
|**Credential Leaks**|Пароли из старых баз, хеши, скомпрометированные аккаунты.|**HaveIBeenPwned**, **DeHashed**, Leak-Lookup.|
### 1.4. Внешний периметр (Service Fingerprinting)

|Подэтап|Что собираем (Цель)|Инструменты|
|---|---|---|
|**IoT/Service Search**|Открытые порты, баннеры сервисов, скриншоты веба (через кэш).|**Shodan**, **Censys**, **ZoomEye**, **URLScan.io**.|
|**Aggregated Recon**|Полная корреляция всех найденных данных в единый граф.|**SpiderFoot**, **BBOT**, **Maltego**.|
### Результат этапа

1. **Scope:** Список подтвержденных IP и доменных имен.
2. **User-List:** Список e-mail и логинов для брутфорса/фишинга.
3. **Password-List:** Пароли из утечек (если найдены).
4. **Tech-Stack:** Версии ОС и сервисов, найденные через метаданные или Shodan.