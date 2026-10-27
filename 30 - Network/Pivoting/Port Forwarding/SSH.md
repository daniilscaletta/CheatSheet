#ssh #forwarding #port 
# Оглавление
- [[#Port Forwarding]]
- [[#SSH Tunneling]]
- [[#ProxyJump]]
- [[#Tunneling]]
- [[#SSH Multyplexing]]

# Port Forwarding
## 1) -L 

**ЛОКАЛЬНЫЙ ПРОБРОС ПОРТА**
```bash
ssh -L [мой_адрес:]мой_порт:их_хост:их_порт user@ssh_сервер
```

|Пара|Чья|Что значит|
|---|---|---|
|`localhost:1234`|**Моя** машина|SSH-клиент слушает этот порт у меня|
|`localhost:3306`|**Их** машина|SSH-сервер стучится сюда у себя|

**Как читать:** «Слушай у меня порт 1234 → через SSH → подключись к localhost:3306 на той стороне».

**Зачем:** MySQL слушает только localhost на сервере (снаружи порт 3306 закрыт — видно по nmap). SSH-туннель «просовывает руку» внутрь и достает до него.

**Проверка:** после запуска `mysql -h 127.0.0.1 -P 1234` — ты подключен к удаленной MySQL, как будто она локальная.

**Запомнить:** первый localhost — мой, второй — их. `-L` = Local (у меня).

![[ssh -L.png]]

myComp:1234 -> localhost:3306 (user@server)
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

Используем, когда нам необходимо дать доступ к своему приложению наружу или нужен реверс шел от хоста, у которого до нас нет маршрута

Приложение или listener работает у нас на `localhost:3000`, теперь к нему можно будет достучаться через `server_ip:9000`
```powershell
ssh -R <InternalipPivotHost>:8080:localhost:8000 user@server_ip  
```

Но чаще может понадобиться такой синтаксис
```powershell
ssh -Rv -N 172.16.5.129:8080:0.0.0.0:8000 ubuntu@server_ip 
```
- `172.16.5.129` - внутренний IP машины, чтобы порт `8080` был доступен всем во врутренней сети, а не только на `127.0.0.1`
- `0.0.0.0` - на нашей машине ssh клиент слушает на всех интерфейсах

Теперь маршрут идет наоборот, когда c целевого хосат делают запрос на 172.16.5.129:8080 он через ssh туннель идет к нам на локальный хост на порт  localhost:8000, на котором доложен быть установлен слушатель 

## 3) -D

**ДИНАМИЧЕСКИЙ ПРОБРОС ПОРТОВ**

В случае, если нам нужно получить доступ не к одному порту - одной службе, а полность к сети, например, для ее скана, то необходимо использовать `dynamic port forwarding`, через SOCKS5 

> То же что и -L, но для всей полдсети

![[ssh -D.png]]
 
`-D` - Этот аргумент запрашивает у SSH-сервера включение динамической переадресации портов
```bash
ssh -NfD 1080 user@server  
```
То есть мы открываем у себя порт локально, через который смотрим во внутреннюю сеть целевого сервера

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
### **ProxyJump**

В ~/.ssh/config:
```bash
Host internal-server
    HostName internal.example.com
    User user
    ProxyJump bastion-user@bastion.example.com
```
Достаточно одной команды ssh internal-server, и соединение пройдёт через bastion автоматически

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