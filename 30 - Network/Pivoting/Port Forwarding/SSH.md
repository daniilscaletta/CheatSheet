#ssh #forwarding #port 


# Оглавление




# Port Forwarding
## 1) -L 

**ЛОКАЛЬНЫЙ ПРОБРОС ПОРТА**

Доступ к локальному сервису через внешний порт

Используем, когда нужно получить доступ к внутреннему сервису на localhost:3306, который не торчит наружу
Для этого открываем порт 1234 и теперь через него могу уже обращаться к службе на 3306

![[ssh -L.png]]

server:1234 -> localhost:3306
```bash
ssh -L 1234:localhost:3306 user@server  
```

Можно перенаправить несколько портов
```bash
 ssh -L 1234:localhost:3306 -L 8080:localhost:80 ubuntu@server
```

## 2) -R 

**УДАЛЕННЫЙ ПРОБРОС ПОРТА**

![[ssh -R.png]]

Используем, когда нам необходимо дать доступ к своему приложению наружу

Приложение работает у нас на `localhost:3000`, теперь к нему можно будет достучаться через `server_ip:9000`
```powershell
ssh -R 9000:localhost:3000 user@server_ip  
```

Но чаще может понадобиться такой синтаксис
```powershell
ssh -Rv -N 172.16.12.6:8080:0.0.0.0:8000 ubuntu@server_ip 
```
- `172.16.12.6` - внутренний IP машины, чтобы порт `8080` был доступен всем во врутренней сети, а не только на `127.0.0.1`
- `0.0.0.0` - на нашей машине ssh клиент слушает на всех интерфейсах


## 3) -D

**ДИНАМИЧЕСКИЙ ПРОБРОС ПОРТОВ**

В случае, если нам нужно получить доступ не к одному порту - одной службе, а полность к сети, например, для ее скана, то необходимо использовать `dynamic port forwarding`, через SOCKS5 

![[ssh -D.png]]
 
`-D` - Этот аргумент запрашивает у SSH-сервера включение динамической переадресации портов
```bash
ssh -NfD 1080 user@server  
```

Далее нам необходим инструмент, способный маршрутизировать пакеты любого инструмента через этот порт - `proxychains`
для этого изменяем конфиг 

`/etc/proxychains.conf`
```bash
socks5  127.0.0.1 9050
```

Далее делаем что хотим

<span style="background:#b1ffff">> В ЧЕМ ПЛЮСЫ: </span>
<span style="background:#b1ffff">> 1) НЕ ПАЛИМ IP</span>
<span style="background:#b1ffff">> 2) ИСПОЛЬЗУЕМ ИНСТРУМЕНТЫ СО СВОЕЙ ТАЧКИ</span>

```bash
proxychains nmap -Pn -p3389 172.16.5.19
```

```powershell
proxychains xfreerdp3 /v:172.16.5.19  /u:victor /p:pass@123 
```








### **SSH Tunneling**

**ДЛЯ A&D:**
Cоздаю туннель через drop@spbctf.bbctf.ru 
При подключении на drop@spbctf.bbctf.ru на порт 3231 трафик ssh будет перенаправлен на вулнбокс 7.7.7.1:22

```bash
ssh -NfR 0.0.0.0:3231:7.7.7.1:22 drop@spbctf.bbctf.ru
```


**ДЛЯ ЛЮБОГО ТУННЕЛЯ:**
Теперь через порт 1080 нам доступны все сервисы сервера root@45.95.235.23
Для этого нужно подключиться через прокси на 1080, либо: 

curl --socks5-hostname localhost:1080 "http://[fd66:666:325::2]:3000/"
```bash
ssh -NfD 1080 root@45.95.235.23
```

### **ProxyJump**

В ~/.ssh/config:
```bash
Host internal-server
    HostName internal.example.com
    User user
    ProxyJump bastion-user@bastion.example.com
```
Достаточно одной команды ssh internal-server, и соединение пройдёт через bastion автоматически


### Tunneling

Доступ к удаленному через локальный
localhost:8080 -> server:80
```bash
ssh -L 8080:localhost:80 user@server  
```

Проброс с сервера на клиент
```bash
ssh -R 9090:localhost:3000 user@server  
```

SOCKS Proxy
```bash
ssh -D 1080 user@server  
```


### SSH Multyplexing

1) Создаём папку под сокеты:
```bash
mkdir -p ~/.ssh/sockets
chmod 700 ~/.ssh/sockets
```
2) Добавляем в ~/.ssh/config:
```bash
Host myserver
    HostName 192.168.1.10
    User admin
    ControlMaster auto
    ControlPath ~/.ssh/sockets/%r@%h:%p
    ControlPersist 10m
```
3) Работаем
```bash
ssh myserver # подключение за доли секунды
```



## **pssh**

```bash
pssh -h hosts.txt -i "systemctl status nginx"
```

```bash
pscp -h hosts.txt local.conf /etc/myapp/config.conf
```