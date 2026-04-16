#tool #windows #AD #cyberkillchain #lolbin #enum

# WMIC (Windows Management Instrumentation Command-line)

> **WMIC** — это консольная утилита, предоставляющая интерфейс командной строки к инфраструктуре **WMI** (Windows Management Instrumentation). Она позволяет управлять локальными и удаленными системами Windows, запрашивать данные о железе, софте, процессах и изменять настройки ОС без использования графического интерфейса.

### Как он работает

Инструмент обращается к базе данных **CIM** (Common Information Model).

1. **Локально:** Прямое обращение к репозиторию WMI.

2. **Удаленно:** Использует протокол **RPC/DCOM** (порт **135** для инициации сессии + динамические порты для передачи данных).

3. **Объекты:** Все данные в WMI разбиты на **классы** (например, `Win32_Process`), а WMIC использует **псевдонимы (aliases)** для упрощения доступа (например, просто `process`).

## Эксплуатация

### 1. Enumeration

_Самый тихий и эффективный способ разведки «на месте»._

- **Версия ОС и архитектура:** 
```powershell
wmic os get caption, version, osarchitecture
```

- **Список установленных патчей (Hotfixes):** 
```powershell
wmic qfe get caption, description, hotfixid, installedon
```

- **Данные о дисках:** 
```powershell
wmic logicaldisk get deviceid, freespace, size, description
```

### 2. Управление процессами и софтом

_Позволяет понять, что запущено и что можно атаковать._

- **Список процессов с путями к .exe:** 
```powershell
wmic process get name, executablepath, processid
```

- **Удаленное завершение процесса:** 
```powershell
wmic process where name="calc.exe" delete
```

- **Список установленного ПО:** 
```powershell
wmic product get name, version
```

### 3. Продвижение (Lateral Movement)

_Использование WMIC для атаки на другие хосты в домене 
(требуются права администратора)._

- **Удаленный запуск команды:** 
```powershell
wmic /node:"TARGET_IP" process call create "C:\Windows\System32\cmd.exe /c whoami > C:\pwn.txt"
```

- **Просмотр шар на удаленной машине:** 
```powershell
wmic /node:"TARGET_IP" share get name, path
```

### 4. Работа с целями

- `useraccount`: **Работа с учетками (SID, статус, домен).**
- `group`**Просмотр групп пользователей.**
- `sysaccount`**Системные учетные записи (System, Network Service).**
- `netlogin`**Данные о последнем входе пользователей (время, количество входов).