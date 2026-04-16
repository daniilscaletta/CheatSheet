#windows #AD #creds 

# Sticky Notes Passwords

БД приложение, в которой могут храниться пароли 
```powershell
ls C:\Users\<user>\AppData\Local\Packages\Microsoft.MicrosoftStickyNotes_8wekyb3d8bbwe\LocalState\plum.sqlite
```

Далее любым способом переносим на хост машину или через base64
```powershell
[Convert]::ToBase64String([IO.File]::ReadAllBytes("C:\path\to\secret.txt"))
```

```bash
echo "ТВОЙ_BASE64_КОД" | base64 -d > secret.txt
```
открываем в браузере DB Sqlite

# Другие интересные файлы

```powershell
%SYSTEMDRIVE%\pagefile.sys 
%WINDIR%\debug\NetSetup.log 
%WINDIR%\repair\sam 
%WINDIR%\repair\system 
%WINDIR%\repair\software, %WINDIR%\repair\security 
%WINDIR%\iis6.log 
%WINDIR%\system32\config\AppEvent.Evt 
%WINDIR%\system32\config\SecEvent.Evt 
%WINDIR%\system32\config\default.sav 
%WINDIR%\system32\config\security.sav 
%WINDIR%\system32\config\software.sav 
%WINDIR%\system32\config\system.sav 
%WINDIR%\system32\CCM\logs\*.log 
%USERPROFILE%\ntuser.dat 
%USERPROFILE%\LocalS~1\Tempor~1\Content.IE5\index.dat %WINDIR%\System32\drivers\etc\hosts 
C:\ProgramData\Configs\* 
C:\Program Files\Windows PowerShell\*
```