#powershell

# Команды

| **PowerShell (Cmdlet)** | **PowerShell (Alias)**                                     | **cmd**               | **Bash**       | **Описание**                                                                                                                    |
| ----------------------- | ---------------------------------------------------------- | --------------------- | -------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| Get-Location            | gl, pwd                                                    | cd                    | pwd            | Отображает текущий рабочий каталог.                                                                                             |
| Set-Location            | sl, cd, chdir                                              | cd, chdir             | cd             | Меняет текущий каталог.                                                                                                         |
| Clear-Host              | cls, clear                                                 | cls                   | clear          | Очищает экран.                                                                                                                  |
| Copy-Item               | cpi, copy, cp                                              | copy                  | cp             | Копирует один, несколько файлов или дерево каталогов (в _PowerShell_ также можно копировать объекты других поставщиков данных). |
| Get-Help                | help, man                                                  | help                  | man            | Справка по командам.                                                                                                            |
| Remove-Item             | ri, del, erase, rmdir, rd, rm                              | del, erase, rmdir, rd | rm, rmdir      | Удаляет файл/каталог (или другой элемент в поставщиках данных _PowerShell_).                                                    |
| Rename-Item             | rni, ren                                                   | ren, rename           | mv.            | Переименовывает файл/каталог.                                                                                                   |
| Move-Item               | mi, move, mv.  -Recurse                                    | move                  | mv.       -r   | Перемещает файл/каталог.                                                                                                        |
| Get-ChildItem           | gci, dir, ls.        -Force                                | dir                   | ls          -a | Выводит все файлы/каталоги в текущем каталоге.                                                                                  |
| Write-Output            | echo, write                                                | echo                  | echo           | Выводит строки, переменные на стандартный вывод.                                                                                |
| Pop-Location            | popd                                                       | popd                  | popd           | Изменяет текущий каталог на тот, который был последним помещён в стек.                                                          |
| Push-Location           | pushd                                                      | pushd                 | pushd          | Помещает текущий каталог в стек.                                                                                                |
| Set-Variable            | sv, set                                                    | set                   | set            | Установка значения переменной/создание переменной.                                                                              |
| Get-Content             | gc, type, cat                                              | type                  | cat            | Получает содержимое файла.                                                                                                      |
| ==Select-String==       | ==sls==                                                    | ==find, findstr==     | ==grep==       | ==Выводит строки, подходящие под условие.==                                                                                     |
| Get-Process             | gps, ps                                                    | tlist, tasklist       | ps             | Выводит все запущенные процессы.                                                                                                |
| Stop-Process            | spps, kill                                                 | kill, taskkill        | kill           | Останавливает запущенный процесс.                                                                                               |
| Tee-Object              | tee                                                        | n/a                   | tee            | Передает входные данные в файл или переменную, затем передает их дальше по конвейеру.                                           |
| New-Item                | ni hello.txt -ItemType File   ni hello -ItemType Directory |                       | touch          | Создание пустого файла/директории                                                                                               |

# Параметры

```powershell
-<parameter_name> <parameter_value>
-<parameter_name>:<parameter_value>
```

```powershell
Set-Alias -Name gprcss -Value  Get-Process
```

Некоторые параметры можно иногда опускать
```powershell
Set-Alias gprcss Get-Process
```

# Конвейер 

Как в Bash

```powershell
ipconfig | sls IPv6
```


# Переменные

Переменные обозначаются префиксом `$`. Переменные могут иметь значения базовых типов или объектов. Строки заключаются в кавычки. Двойные кавычки заменяют имена переменных в строке на их значения.

- Переменная `$args` содержит массив всех неименованных аргументов командной строки.
- Переменная `$_` возвращает ссылку на текущий объект в конвейере.
- Аналогично `%` означает `ForEach` для работы итерации в массивах.
- Фигурные скобки `{ }`, обрамляющие путь к файлу, позволяют обратиться к содержимому этого файла, в том числе записать туда значение переменной.
- К свойства и методам объекта по аналогии с _C#_ позволяет обратиться точка.
- Фильтр вывода `Where-Object` можно заменить алиасом `?`.

# Переменные среды

Список всех
```powershell
Get-Item Env:
```

Просмотреть переменную
```powershell
$Env:path
```

Задать переменную
```powershell
$Env:<variable-name> = "<new-value>"
```

Добавить значение в переменную
```powershell
Env:PSModulePath += ";c:\Modules"
```

Изменения переменных действуют только в рамках текущей сессии. Постоянные изменения выполняются с использованием методов `System. Environment` и с правами администратора.

```powershell
[Environment]::SetEnvironmentVariable("PSModulePath", 'C:\PS\Modules', 'Machine')
```

Здесь третий параметр `Machine` означает, что данное изменение применяется на локальном компьютере. Другим параметром может быть `User`, в таком случае изменения будут применяться к текущему пользователю.

# Функции

Разрешение на выполнение сценариев (chmod +x)

```powershell
Set-ExecutionPolicy Bypass
```

_PS_ позволяет создавать и использовать собственные функции. Аргументы функций, в отличие от других командных интерпретаторов, разделяются пробелами.

- `<function> <param1> <param2>` — функция с двумя аргументами.
- `<function>(<param1>, <param2>)` — функция с одним аргументом, массивом из двух элементов.

Стандартное задание функции выглядит следующим образом:
```powershell
Function TestPath ([String]$Path)
        {
                Return(Test-Path $Path)
        }
```

В круглых скобках задаются переменные. 
В теле функции задаются необходимые командлеты для выполнения. 
`Return` позволяет вывести значение из функции.

Удачные функции можно выносить в отдельный `.ps1`-файл для последующего обращения извне. В файл записываем только саму функцию без вызова:
```powershell
function ExtendDisk-Remotely
{
    param (
     [Parameter (Mandatory = $true)]
        [string] $ComputerName,
     [Parameter (Mandatory = $false)]
        [string] $DiskDrive = "c"
    )

    Invoke-Command -ComputerName $ComputerName -ScriptBlock {"rescan", "select volume=$using:DiskDrive", "extend" | diskpart}
}
```

Обращение к файлам (ДотСорсинг)
```powershell
. C:\PS\Example.ps1
```

# Модули

Прописывать путь к файлу может быть удобно для статического администрирования, но не очень удобно для динамического пентеста. Оптимизировать процесс реиспользования кода помогают модули.

**Модули** — это те же вынесенные в файлы функции, но лежащие в папках по умолчанию. Расширение файла меняется при этом на `.psm1`. Пути до этих папок можно менять по всей сети, получая параллельный доступ к модулям, обращаясь в дальнейшем только по имени функции без пути.

Текущий путь содержит переменная `PSModulePath`. Выведем её содержимое:
```powershell
$Env:PSModulePath
```

Кроме редактирования переменной среды, как мы узнали выше, пути можно редактировать массово через _GPO_ или раскидывать файлы по полученным папкам.

Функции из модуля можно вызывать без предварительного объявления модуля.

С помощью модулей можно также расширять возможности _PowerShell_, импортируя новые командлеты. Поместите модуль с нужными командлетами в одну из папок, указанную в `PSModulePath`. В папке модуля должен содержаться файл манифеста модуля (`.psd1`).

Файл манифеста в текстовом виде содержит описание модуля и способ его сборки. В нём также содержится хэш-таблица ключей и значений. Манифест модуля можно создать автоматически командлетом `New-ModuleManifest` с указанием имени файла манифеста:

```powershell
New-ModuleManifest -Path C:\NewModule.psd1 -ModuleVersion "2.0" -Author "Ivan"
```

Для большинства версий _PowerShell_ этого достаточно. Командлеты из модуля будут импортированы автоматически при использовании командлета или функции. Но на всякий случай и для старых версий дополнительно нужно ввести команду:
```powershell
Import-Module [Module_Name]
```
После установки модуля можно использовать указанные в нём командлеты как обычные.

# Командлеты для Пентеста 

## Оглавление
- [[#New-PSSession (nsn) (Аналог `nc`)]]
- [[#Test-NetConnection (tnc) (Замена `ping`, `traceroute`, сканер портов и `telnet`)]]

---

## New-PSSession (nsn) (Аналог `nc`)

Командлет устанавливает постоянное фоновое удалённое подключение к другому _Windows_-хосту. Причём подключиться можно одновременно к нескольким хостам:
```powershell
New-PSSession -ComputerName Server01, Server02
```

Укрощено
```powershell
nsn server1 -Credentials domain\admin
```

Подключение ко всем хостам домена AD
```powershell
Get-ADComputer -Filter * -Properties name | select @{Name="ComputerName";Expression={$_."name"}} | nsn
```

Помещение сессий в отдельную переменную для работы с ними
```powershell
$session = nsn Server01, Server02
```

После установки сеанса командлеты выполняются через `Invoke-Command` (Алиас: `icm`), результаты также можно передавать через пайп в другой командлет.
```powershell
Invoke-Command {Get-ChildItem} -session $session -AsJob
```

Параметр `-AsJob` указывает, что команда выполняется в фоновом режиме.

Через `Invoke-Command` можно передавать модули и собственные командлеты.
```powershell
icm {Import-Module ActiveDirectory} -session $session
```

Также можно запускать локальные скрипты:
```powershell
icm -ComputerName Server01 -FilePath C:\PSpentest\Mimikatz.ps1
```

## Test-NetConnection (tnc) (Замена `ping`, `traceroute`, сканер портов и `telnet`)

1) Детальный пинг
```powershell
tnc skillfactory.ru -I Detailed
```

2) Расширенный скан портов
```powershell
tnc 10.10.1.7 -p 3389 -I Detailed
```

3) Трассировка
```powershell
tnc skillfactory.ru -T
```

4) Скан сети на открытые порты
```powershell
foreach ($ip in 0..255) {tnc -P 3389 -I "Detailed" 10.10.1.$ip}
```

5) Сканер хоста по портам
```powershell
foreach ($port in 1..500) {if (($a=tnc 10.10.1.7 -P $port -Wa SilentlyContinue).tcpTestSucceeded -eq $true){ "Open: $port"}}
```
