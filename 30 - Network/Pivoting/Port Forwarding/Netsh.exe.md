#tunneling #forwarding #windows 

> Netsh.exe - это инструмент командной строки Windows, который может помочь в настройке сети в конкретной системе Windows
> Инструмент обеспечивает перенаправление портов 

Он также обеспечивает удобное соединение между хостами

Устанавливает  соединение между внутренним хостом и промежуточным
```powershell
netsh.exe interface portproxy add v4tov4 listenport=8080 listenaddress=10.129.15.150 connectport=3389 connectaddress=172.16.5.25
```
Далее подключаемся уже к этому сокету
```bash
xfreerdp3 /v:10.129.15.150:8080 /u:victor /p:pass@123
```


Просмотр установленного соединения
```powershell
netsh.exe interface portproxy show v4tov4
```

Проброс порта из Windows в WSL
```powershell
netsh.exe interface portproxy add v4tov4 listenport=443 listenaddress=192.168.200.1 connectport=443 connectaddress=172.22.70.196
```

Далее при необходимости подключиться на `172.16.5.25:3389` (Который нам не доступен), мы можем подключиться на `10.129.15.150:8080` 