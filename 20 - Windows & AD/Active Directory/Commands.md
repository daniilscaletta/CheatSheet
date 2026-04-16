#AD #windows 

## Оглавление
- [[#Необходимые основные команды]]
- [[#Команды PowerShell для Active Directory]]
  - [[#Команды пользователя AD]]
  - [[#Команды групп AD]]
  - [[#Команды групповых политик (GPO)]]
  - [[#Компьютерные команды]]

---

## Необходимые основные команды

`xfreerdp /v:<IP> /u:<User> /p:<Password>`  
`ping <IP>`

---

## Команды PowerShell для Active Directory

---

### Команды пользователя AD

Добавьте пользователя в Active Directory и задайте его атрибуты.
```powershell
New-ADUser -Name "first last" -Accountpassword (Read-Host -AsSecureString "Super$ecurePassword!") -Enabled $true -OtherAttributes @{'title'="Analyst";'mail'="f.last@domain.com"}
```  

Удаляет пользователя из Active Directory с идентификатором 'name'.
```powershell
Remove-ADUser -Identity <name>
```
  
Разблокирует учетную запись пользователя с именем 'name'.
```powershell
Unlock-ADAccount -Identity <name>
```  

Установите пароль пользователя Active Directory равным указанному паролю.
```powershell
Set-ADAccountPassword -Identity <'name'> -Reset -NewPassword (ConvertTo-SecureString -AsPlainText "NewP@ssw0rdReset!" -Force)
```

Принудительно изменить пароль пользователя при следующей попытке входа в систему.
```powershell
Set-ADUser -Identity amasters -ChangePasswordAtLogon $true
```

---

### Команды групп AD

Создайте новый контейнер подразделения Active Directory с именем "name" по указанному пути.
```powershell
New-ADOrganizationalUnit -Name "name" -Path "OU=folder,DC=domain,DC=local"
```  

Создайте новую группу безопасности с именем "name" и следующими атрибутами.
```powershell
New-ADGroup -Name "name" -SamAccountName analysts -GroupCategory Security -GroupScope Global -DisplayName "Security Analysts" -Path "CN=Users,DC=domain,DC=local" -Description "Members of this group are Security Analysts under the IT OU"
```  

Добавить пользователя Active Directory в указанную группу.
```powershell
Add-ADGroupMember -Identity 'group name' -Members 'ACepheus,OStarchaser,ACallisto'
```

---

### Команды групповых политик (GPO)

Скопируйте объект групповой политики (GPO) для использования в качестве нового объекта групповой политики с целевым именем "name".
```powershell
Copy-GPO -SourceName "GPO to copy" -TargetName "Name"
```

Связывает существующую групповую политику с указанным путем к организационной единице. Параметр "-LinkEnabled Yes" гарантирует, что после установления связи групповая политика и ее правила будут фактически включены (поскольку возможно, что связь между групповыми политиками существует, но одновременно отключена).
```powershell
New-GPLink -Name "Security Analysts Control" -Target "ou=Security Analysts,ou=IT,OU=HQ-NYC,OU=Employees,OU=Corp,dc=INLANEFREIGHT,dc=LOCAL" -LinkEnabled Yes
```  

Привяжите существующую групповую политику (GPO) для использования с определенным организационным подразделением (OU) или группой безопасности.
```powershell
Set-GPLink -Name "Security Analysts Control" -Target "ou=Security Analysts,ou=IT,OU=HQ-NYC,OU=Employees,OU=Corp,dc=INLANEFREIGHT,dc=LOCAL" -LinkEnabled Yes
```

---

### Компьютерные команды


Добавьте новый компьютер в домен, используя указанные учетные данные.
```powershell
Add-Computer -DomainName 'INLANEFREIGHT.LOCAL' -Credential 'INLANEFREIGHT\HTB-student_adm' -Restart
```

Удаленное добавление компьютера в домен.
```powershell
Add-Computer -ComputerName 'name' -LocalCredential '.\localuser' -DomainName 'INLANEFREIGHT.LOCAL' -Credential 'INLANEFREIGHT\htb-student_adm' -Restart
``` 
  
Найдите компьютер с именем "name" и просмотрите его свойства.
```powershell
Get-ADComputer -Identity "name" -Properties * | select CN,CanonicalName,IPv4Address
```