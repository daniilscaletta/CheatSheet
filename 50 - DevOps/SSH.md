#ssh #forwarding #port 
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