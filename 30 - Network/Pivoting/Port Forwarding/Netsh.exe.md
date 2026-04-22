#tunneling #forwarding #windows 

> Netsh.exe - это инструмент командной строки Windows, который может помочь в настройке сети в конкретной системе Windows

Он также обеспечивает удобное соединение между хостами

Устанавливает  соединение между внутренним хостом и промежуточным
```powershell
netsh.exe interface portproxy add v4tov4 listenport=8080 listenaddress=10.129.15.150 connectport=3389 connectaddress=172.16.5.25
```

Просмотр установленного соединения
```powershell
netsh.exe interface portproxy show v4tov4
```

Далее при необходимости подключиться на `172.16.5.25:3389` (Который нам не доступен), мы можем подключиться на `10.129.15.150:8080` 