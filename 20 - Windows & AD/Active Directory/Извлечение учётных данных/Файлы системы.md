
### 1) История команд пользователя

```powershell
C:\Users\<USER>\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt
```

### 2) Поиск слов в реестре

```powershell
reg query HKLM /f <password> /t REG_SZ /s

reg query HKCU /f <password> /t REG_SZ /s
```

### 3) Вывод всех событий безопасности (Логон, выход и тд)

```powershell
wevtutil qe Security /rd:true /f:text | Select-String "/user"

# Process Command Line:   "C:\Windows\system32\findstr.exe" /user
# Process Command Line:   cmdkey  /add:WEB01 /user:amanda /pass:Passw0rd!
# Process Command Line:   net  use T: \\fs01\backups /user:tim MyStr0ngP@ssword
```