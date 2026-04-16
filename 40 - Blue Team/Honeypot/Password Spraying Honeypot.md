#honeypot #defense #monitoring 

Создаем поддельную УЗ с простым паролем (можно не очень)

А далее начинаем аудит этих событий

Успешным входом в систему считаются события с идентификаторами 4624, 4768 и 4769.

- 4624 (Успех): Вход в систему аудита
- 4768 (Успех): Аудит службы аутентификации Kerberos
- 4769 (Успех): Аудит операций с сервисными билетами Kerberos

Неудачные попытки входа в систему имеют идентификаторы 4625 и 4771.

- 4625 (Сбой): Вход в систему аудита
- 4771 (Сбой): Аудит службы аутентификации Kerberos


## Скрипт для создания похожей на реальную УЗ-ловушку

```powershell
Param
 (
    $Domain,
    $UserName,
    $Password
 )

$DCName = (Get-ADDomainController -Discover -DomainName $Domain).Name
$RemotePath = "\\$DCName\SYSVOL"

$UserInfo = Get-ADUser $UserName -Prop LastLogonDate,Enabled -Server $DCName
Write-host "Authenticating as $UserName in $domain (Last Logon Date:$($UserInfo.LastLogonDate) )..." 

$PasswordSS = ConvertTo-SecureString $Password -AsPlainText -Force
$Credential = New-Object System.Management.Automation.PSCredential($UserName, $PasswordSS)
New-SmbMapping -RemotePath $RemotePath -Credential $Credential -ErrorAction Stop
Remove-SmbMapping -RemotePath $RemotePath -Force

$UserInfo = Get-ADUser $UserName -Prop lastLogon -Server $DCName
Write-host "$UserName last authenticated to $DCName on $([datetime]::FromFileTimeUTC($UserInfo.lastLogon)) (UTC)" 
```

А также можно создать в SYSVOL файл group.xml

```xml
<?xml version="1.0" encoding="utf-8" ?>
<Groups clsid="{3125E937-EB16-4b4c-9934-544FC6D24D26}">
<User clsid="{DF5F1855-51E5-4d24-8B1A-D9BDE98BA1D1}" name="Administrator (built-in)" image="2" changed="2019-03-17 03:17:23" uid="{D5FE7352-81E1-42A2-B7DA-118402BE4C33}">
<Properties action="U" newName="TRDAdmin" fullName="" description="Standard Admin Account" cpassword="RI133B2Wl2CiIOCau1DtrtTe3wdFwzCiWB5PSAxXMDstchJt3bLOUie0BaZ/ 7rdQiuqTonF3ZWAKa1iRvd4JGQ" changelogon="0" noChange="0" neverExpires="0" acctDisabled="0" subAuthority="RID_ADMIN" userName="Administrator (built-in)" expires="2019-03-16" />
</User>
</Groups>
```
