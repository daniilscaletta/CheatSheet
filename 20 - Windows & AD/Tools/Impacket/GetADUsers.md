#tool #AD #ldap #windows 

`impacket-GetADUsers` — это утилита из набора **[[Impacket]]**, которая позволяет получить список пользователей из Active Directory по протоколу LDAP

## Оглавление
- [[#Как работает]]
- [[#Эксплуатация]]

---

## Как работает

1. Подключается к контроллеру домена через LDAP
2. Аутентифицируется (NTLM или Kerberos)
3. Выполняет LDAP-запрос на получение объектов типа `user`
4. Возвращает атрибуты:
    - `sAMAccountName`
    - `mail`
    - `lastLogon`
    - `pwdLastSet`
    - `SPN` (если есть)
    - и другие

Внутри — обычный LDAP query к AD. Никакой магии. Просто аккуратная обёртка над протоколом.

## Эксплуатация 

```bash
impacket-GetADUsers <domain>/<user>:<password> -dc-ip <DC_IP> -all -outputfile <output.file> 
```

