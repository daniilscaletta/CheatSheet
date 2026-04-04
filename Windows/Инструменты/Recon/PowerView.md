#recon #tool #AD #windows 

> Инструмент перечисления и разведки в AD Windows

# Эксплуатация

Подключение
```bash
Import-Module .\PowerView.ps1
```

## <span style="background:rgba(205, 244, 105, 0.55)">О Домене</span>
Просмотр политики домена
```powershell
Get-DomainPolicy
```

Базовая инфа о домене
```powershell
Get-NetDomain
```

Список всех DC
```powershell
Get-DomainController
```

Проверка Антивируса, работает ли
```powershell
Get-MpComputerStatus
```
## <span style="background:rgba(205, 244, 105, 0.55)">О Пользователях</span>

Просмотр всей инфы конкретного пользователя
```powershell
Get-DomainUser -Identity mmorgan
```

Просмотр УЗ с `Сonstrained Delegated`
```powershell
Get-DomainUser -TrustedToAuth

# Через Powershell

Get-ADUser -Filter "msds-allowedtodelegateto -like '*'" -Properties msDS-allowedtodelegateto | ` Select-Object Name, msDS-allowedtodelegateto | ` Format-Table -AutoSize
```

Просмотр объектов с определенными свойствами 
- Необязательный пароль (`PASSWD_NOTREQD`)
```powershell
Get-NetUser | Where-Object {$_.useraccountcontrol -like "*PASSWD_NOTREQD*"} | Select-Object samaccountname, useraccountcontrol
```

- Уязвим к AS-REP ROASTING (`DONT_REQ_PREAUTH`)
```powershell
Get-NetUser | Where-Object {$_.useraccountcontrol -like "*DONT_REQ_PREAUTH*"} | Select-Object samaccountname, useraccountcontrol
```

- Unconstrained delegation (`TRUSTED_FOR_DELEGATION`)
```powershell
Get-NetUser | Where-Object {$_.useraccountcontrol -like "*TRUSTED_FOR_DELEGATION*"} | Select-Object samaccountname, useraccountcontrol
	
# или

Get-DomainComputer -Unconstrained Select-Object name
```

- Resource-Based Constrained Delegation (RBCD) (`msDS-AllowedToActOnBehalfOfOtherIdentity`)
```powershell
Get-ADUser -Filter "msDS-AllowedToActOnBehalfOfOtherIdentity -like '*'" -Properties msDS-AllowedToActOnBehalfOfOtherIdentity | ` Select-Object Name, msDS-AllowedToActOnBehalfOfOtherIdentity | ` Format-Table -AutoSize
```

Просмотр УЗ с функцией `gMSA`
```powershell
Get-DomainObject -Properties samaccountname, description, msDS-GroupManagedServiceAccount | ` Where-Object { $_."msDS-GroupManagedServiceAccount" -ne $null } | ` Select-Object samaccountname, description
```

Узнать в каких группах состоит данный пользователь
```powershell
Get-DomainGroup -MemberIdentity "mlowe" | Select-Object samaccountname, distinguishedname
```

## <span style="background:rgba(205, 244, 105, 0.55)">О Компютерах и Сессиях</span>
Быстрый поиск только серверов
```powershell
Get-NetComputer -OperatingSystem "*Server*"
```

Показывает кто сейчас подключен к данному компьютеру
```powershell
Get-NetSession -ComputerName <Name>
```

Показывает, есть ли у тебя права локального администратора на других машинах
```powershell
Find-LocalAdminAccess
```

Проверка наличия доступа локального админа
```powershell
Test-AdminAccess -ComputerName ACADEMY-EA-MS01
```
## <span style="background:rgba(205, 244, 105, 0.55)">О Группах и Правах</span>
Список всех групповых политик
```powershell
Get-NetGPO
```

Удобный просмотр имен и других параметров групповых политик
```powershell
Get-NetGPO | Select-Object displayname
```

Просмотр разрешений (ACL) для конкретного объекта. Помогает найти скрытые права (например, кто может сбросить пароль админу).
```powershell
Get-DomainObjectAcl -Identity "Admin Account"
```

Просмотр всех ACE (ACL) конкретного пользователя
```powershell
$sid = Convert-NameToSid tpetty
Get-DomainObjectACL -Identity * | ? {$_.SecurityIdentifier -eq $sid}
```

Просмотр всех, кто содержится в данной группе
```powershell
Get-NetGroupMember -Identity "Domain Admins" -Recurse | Select-Object MemberName, MemberSid
```

