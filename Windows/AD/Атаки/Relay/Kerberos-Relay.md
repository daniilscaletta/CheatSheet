#kerberos #windows #attacks #AD 

> Kerberos Relay — теоретическая разновидность MITM атаки, при которой атакующий пытается использовать Kerberos-аутентификацию клиента для доступа к другому сервису.  
> 
> В классическом виде практически невозможен из-за архитектуры Kerberos (SPN binding и mutual authentication).

# Почему классический Kerberos Relay не работает

В отличие от NTLM, Kerberos использует **service tickets**, которые криптографически привязаны к конкретному сервису (SPN).

Service Ticket содержит:
- имя пользователя
- SPN сервиса
- session key
- зашифрован ключом сервиса

Даже если атакующий перехватит:

> AP-REQ:  
    Service Ticket  
    Authenticator

он не сможет использовать его на другом сервисе, потому что
- ticket зашифрован ключом конкретного сервиса
- другой сервис не сможет его расшифровать

## SPN Binding

Ticket создаётся строго для конкретного сервиса:
```
CIFS/server01.corp.local
```

Его нельзя использовать для:
```
LDAP/server01.corp.local  
HTTP/server01.corp.local  
MSSQL/server01.corp.local
```
Kerberos проверит SPN и отклонит запрос.

## Mutual Authentication

Kerberos использует взаимную аутентификацию:
```
Client → Service  
AP-REQ  
  
Service → Client  
AP-REP
```

AP-REP зашифрован session key.

Атакующий не знает session key и не может:
- расшифровать AP-REP
- подделать AP-REP
- завершить relay

## Session Key Requirement

Session key известен только:
```
Client  
Service
```

Атакующий не имеет session key, поэтому не может:
- создать authenticator
- установить новую Kerberos сессию
- использовать ticket