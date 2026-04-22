#tool #icmp #tunneling 

> Туннелирование ICMP инкапсулирует трафик внутри сети в`ICMP packets`содержащие `echo requests` и `responses`
> Туннелирование ICMP будет работать только в том случае, если в сети с брандмауэром разрешены ответы на ping-запросы

# Настройка туннеля

1) Установка 
```bash
git clone https://github.com/utoni/ptunnel-ng.git

sudo ./autogen.sh
```

2) Доставка инструмента на `pivot` хост
```bash
scp -r ptunnel-ng ubuntu@10.129.202.64:~/
```

3) На `pivot` хосте запускаем
```bash
sudo ./ptunnel-ng -r10.129.202.64 -R22
```
- `10.129.202.64` - ip addr pivot хоста, доступный с хоста атакующего

4) Подключение к серверу с хоста атаки
```bash
sudo ./ptunnel-ng -p10.129.202.64 -l2222 -r10.129.202.64 -R22
```

<span style="background:#40a9ff">ВСЕ! ТОННЕЛЬ СОЗДАН</span>

Далее через него мы можем пускать любой трафик

1) подключение по sh
```bash
ssh -p2222 -lubuntu 127.0.0.1
```

2) динамическая переадресация ssh
```bash
ssh -D 9050 -p2222 -lubuntu 127.0.0.1
```

Передача трафика через `proxychains`
```bash
proxychains nmap -sV -sT 172.16.5.19 -p3389
```