# Windows & AD — MOC

> Самый большой раздел: атаки на Active Directory, Windows OS, инструменты, механизмы аутентификации, извлечение учётных данных, ADCS, Kerberos и многое другое.

## Оглавление
- [[#Active Directory — Основы]]
- [[#Механизмы аутентификации]]
- [[#ADCS (Службы сертификатов)]]
- [[#Smart Cards & PKI]]
- [[#Атаки на AD]]
- [[#Извлечение учётных данных]]
- [[#Известные уязвимости]]
- [[#Hardening AD]]
- [[#Windows OS — Внутреннее устройство]]
- [[#Windows OS — Классы уязвимостей]]
- [[#PowerShell]]
- [[#Инструменты — Recon]]
- [[#Инструменты — Initial Access]]
- [[#Инструменты — Lateral Movement]]
- [[#Инструменты — Post-Exploitation]]
- [[#Инструменты — Pivoting]]
- [[#Инструменты — LPE]]
- [[#Инструменты — Impacket]]
- [[#Инструменты — Support Tools]]

---

## Active Directory — Основы

- [[Общие понятия]] — базовые концепции Active Directory
- [[Безопасность в Windows]] — механизмы безопасности Windows
- [[Механизмы аутентификации в Windows]] — обзор протоколов аутентификации
- [[Делегирование Kerberos]] — типы делегирования и их риски
- [[Trusts]] — доверительные отношения между доменами
- [[Анализ уязвимостей]] — методология анализа уязвимостей AD
- [[Усиление безопасности AD]] — рекомендации по защите
- [[Commands]] — полезные команды для работы с AD
- [[Бинарные атаки]] — атаки на бинарном уровне

**Фазы атаки:**
- [[1. Разведка (Discovery) Enum]] — перечисление объектов AD
- [[2. Горизонтальное перемещение (Lat move)]] — lateral movement в домене
- [[3. Повышение привилегий (LPE)]] — повышение привилегий
- [[4. Закрепление (Persist)]] — persistence в домене

## Механизмы аутентификации

- [[Kerberos]] — протокол Kerberos, структура, билеты
- [[NTLM]] — протокол NTLM, хэши, атаки
- [[LDAP]] — протокол LDAP, запросы, атаки

## ADCS (Службы сертификатов)

- [[Общие сведения]] — введение в ADCS
- [[Архитектура и Компоненты]] — компоненты PKI инфраструктуры
- [[Шаблоны сертификатов (Templates)]] — конфигурация и уязвимости шаблонов
- [[Выпуск сертификата (Enrollment)]] — процесс выпуска сертификатов
- [[Аутентификация (PKINIT & Smart Cards)]] — аутентификация через сертификаты
- [[Проверка отзыва сертификатов (CRL & OCSP)]] — механизмы отзыва
- [[Митигации]] — защита инфраструктуры ADCS
- [[certipy (certifi.exe)]] — инструмент для атак на ADCS

## Smart Cards & PKI

- [[Аутентификация по Смарт картам]] — механизм аутентификации по смарт-картам
- [[Windows Hello (WHfB)]] — Windows Hello for Business
- [[Митигации]] — защита от атак на смарт-карты

## Атаки на AD

**Roasting-атаки:**
- [[Kerberoasting]] — атака на SPN-аккаунты
- [[AS-REP Roasting]] — атака на аккаунты без pre-auth
- [[AS-REQ Roasting]] — атака через AS-REQ

**Pass-the-* атаки:**
- [[Pass-the-Hash]] — передача хэша NTLM
- [[Pass-the-Ticket]] — передача Kerberos-билета
- [[Pass-the-Key (Overpass-the-hash)]] — overpass-the-hash техника

**Relay-атаки:**
- [[NTLM-Relay]] — ретрансляция NTLM-аутентификации
- [[SMB relay]] — relay через SMB
- [[LDAP Relay]] — relay через LDAP
- [[Kerberos-Relay]] — ретрансляция Kerberos

**Другие атаки:**
- [[ACL Abuze]] — злоупотребление ACL в AD
- [[Coerce]] — принудительная аутентификация (PrinterBug, PetitPotam)
- [[DCSync]] — репликация хэшей с DC
- [[DCShadow]] — подмена контроллера домена
- [[DLL Hijacking]] — перехват загрузки DLL
- [[Golden (Silver) Ticket]] — атаки на Kerberos с поддельными билетами
- [[LLMNR , NBT-NS Poisoning]] — отравление LLMNR/NBT-NS
- [[Misconfiguration]] — эксплуатация неправильных конфигураций
- [[Potato Attacks]] — атаки типа Potato (Juicy, Sweet, Hot)
- [[PrintSpoofer]] — эксплуатация PrintSpoofer
- [[Shadow Admins]] — скрытые администраторские аккаунты
- [[Unconstrained Delegation​]] — атака через неограниченное делегирование

## Извлечение учётных данных

- [[lsass.exe]] — дамп LSASS и извлечение учётных данных
- [[NTDS.dit]] — извлечение базы данных AD
- [[SAM SECURITY SYSTEM]] — дамп SAM, SECURITY, SYSTEM
- [[Pillaging]] — сбор данных с захваченного хоста
- [[Учетки в ОС]] — где хранятся учётные данные в Windows
- [[Файлы системы]] — системные файлы с учётными данными
- [[Иные файлы]] — другие файлы с чувствительными данными
- [[Иные способы]] — альтернативные методы извлечения
- [[Автоматизированные инструменты]] — инструменты автоматического извлечения
- [[Монтирование VHDX, VMDK]] — извлечение данных из образов дисков
- [[Механизмы безопасности Windows]] — защитные механизмы и их обход

## Известные уязвимости

- [[BlueKeep]] — CVE-2019-0708, RDP RCE
- [[EternalBlue]] — MS17-010, SMB RCE
- [[NoPac]] — CVE-2021-42278/42287, захват домена
- [[PrintNightmare]] — CVE-2021-1675, LPE/RCE
- [[ProxyLogon]] — CVE-2021-26855, Exchange RCE
- [[SMBGhost]] — CVE-2020-0796, SMB RCE
- [[Zerologon]] — CVE-2020-1472, захват домена

## Hardening AD

- [[Защита в людях]] — организационные меры безопасности
- [[Защита в технологиях]] — технические меры защиты
- [[Коды событий системы безопасности AD]] — Event ID для мониторинга AD

## Windows OS — Внутреннее устройство

**LOLBAS:**
- [[О LOLBAS]] — Living Off The Land Binaries
- [[Certutil.exe]] — злоупотребление certutil
- [[Scheduled Tasks]] — злоупотребление планировщиком задач

**Привилегии и права:**
- [[UAC]] — User Account Control и его обход
- [[О правах и привилегиях]] — обзор системы прав Windows
- [[Важные привилегии]] — привилегии, полезные при атаке
- [[Эксплуатация привилегий]] — техники эксплуатации привилегий

**Права групп:**
- [[Важные группы]] — важные группы Windows
- [[Backup Operators]] — группа Backup Operators
- [[DNS Administrators]] — группа DNS Admins
- [[Server Operators]] — группа Server Operators

**Сетевая подсистема:**
- [[Важные подсистемы]] — важные сетевые подсистемы Windows

## Windows OS — Классы уязвимостей

- [[DLL Injection]] — инъекция DLL
- [[20 - Windows & AD/Windows OS/Классы уязвимостей/Kernel Exploits]] — эксплуатация уязвимостей ядра
- [[Vulnerable Services]] — уязвимые сервисы Windows
- [[Weak Permissions]] — слабые права доступа
- [[Взаимодействия с пользователями]] — атаки через взаимодействие с пользователем

## PowerShell

- [[Работа с оболочкой]] — работа в PowerShell, полезные команды
- [[Фреймворки для пентеста]] — PowerSploit, Empire и другие

## Инструменты — Recon

- [[BloodHound]] — граф атак на AD
- [[PowerView]] — PowerShell-разведка в AD
- [[enum4linux-ng]] — перечисление SMB/Samba
- [[ldapsearch]] — LDAP-запросы
- [[rpcclient]] — разведка через RPC
- [[smbclient]] — доступ к SMB-ресурсам
- [[ADRecon]] — детальный аудит AD
- [[Adalanche]] — визуализация уязвимостей AD
- [[BloodyAD]] — атаки через LDAP
- [[Kerbrute]] — перебор пользователей Kerberos
- [[Pretender]] — MITM в AD-сетях
- [[WMIC]] — Windows Management Instrumentation

## Инструменты — Initial Access

- [[Kerbrute]] — перебор пользователей/паролей Kerberos

## Инструменты — Lateral Movement

- [[CrackMapExec]] — Swiss army knife для AD
- [[NetExec]] — замена CrackMapExec
- [[RunasCs.exe]] — запуск процессов от другого пользователя

## Инструменты — Post-Exploitation

- [[Mimikatz]] — извлечение учётных данных и атаки
- [[Rubeus]] — Kerberos-атаки и манипуляции с билетами
- [[Evil-WinRM]] — удалённый доступ через WinRM
- [[CrackMapExec]] — пост-эксплуатация через SMB/WinRM
- [[NetExec]] — пост-эксплуатация, замена CrackMapExec
- [[WinPwn]] — автоматизация пост-эксплуатации Windows
- [[gpp-decrypt]] — расшифровка паролей из GPP
- [[pyLAPS]] — работа с LAPS
- [[rpcclient]] — операции через RPC
- [[smbclient]] — работа с SMB

## Инструменты — Pivoting

- [[Chisel]] — TCP/UDP туннелирование
- [[Ligolo-ng]] — туннелирование с агентом
- [[GOST]] — многофункциональный прокси/туннель

## Инструменты — LPE

- [[Sherlock]] — поиск LPE-уязвимостей в Windows

## Инструменты — Impacket

- [[GetADUsers]] — перечисление пользователей AD
- [[GetNPUsers]] — AS-REP Roasting
- [[GetUserSPNs]] — Kerberoasting
- [[MSSQLclient]] — подключение к MSSQL
- [[PSexeс]] — удалённое выполнение команд
- [[SecretsDump]] — дамп учётных данных
- [[Ticketer]] — создание Kerberos-билетов
- [[WmiExec]] — выполнение команд через WMI
- [[getST]] — получение сервисных билетов

## Инструменты — Support Tools

- [[ADGenerator.py]] — генерация тестовых AD-сред
- [[KeyDecriptor]] — декодирование ключей
- [[ntlm_theft.py]] — генерация файлов для кражи NTLM-хэшей
