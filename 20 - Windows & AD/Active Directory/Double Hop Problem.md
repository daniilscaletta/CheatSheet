#kerberos #ntlm #doublehop #creds #credentials 


> Проблема «двойного перехода» (Double Hop) — это распространённое ограничение в PowerShell Remoting, суть которого в том, что **ваши учётные данные по умолчанию не могут быть переданы дальше первого удалённого компьютера для аутентификации на втором удалённом компьютере**


# Решения проблемы

### 1) PSCredential object

```powershell
$SecPassword = ConvertTo-SecureString '!qazXSW@' -AsPlainText -Force
$Cred = New-Object System.Management.Automation.PSCredential('INLANEFREIGHT\backupadm', $SecPassword)

Get-DomainUser -spn -credential $Cred | select samaccountname
```
Здесь мы явно передаем учетные данные и выполняемся от них

### 2) RBCD

Указываем ServerC, чтобы он доверял ServerB при подключении
```powershell
Set-ADComputer -Identity ServerC -PrincipalsAllowedToDelegateToAccount ServerB
```

### 3) PSSessionConfiguration

```powershell
Register-PSSessionConfiguration -Name backupadmsess -RunAsCredential inlanefreight\backupadm

Enter-PSSession -ComputerName DEV01 -Credential INLANEFREIGHT\backupadm -ConfigurationName  backupadmsess
```
Здесь мы учетки не передаем и выполняемся от имени промежуточного хоста