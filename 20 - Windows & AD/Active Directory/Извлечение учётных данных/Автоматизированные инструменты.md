#tools #windows #AD #creds 

## Оглавление
- [[#1) Snaffler]]
- [[#2) Spider_plus (Модуль nxc) (аналог Snaffler)]]
- [[#3) LaZagne]]
- [[#4) SessionGopher]]

---

## 1) Snaffler

Поиск кредов, паролей, учеток по всему домену
```powershell
snaffler.exe -s -o snaffler.log
```

## 2) Spider_plus (Модуль nxc) (аналог Snaffler)

```bash
nxc smb <IP> -u <user> -p <pass> -M spider_plus
```

## 3) LaZagne

Ищет все учетку в рамках локальной машины из всех приложений, файлов, папок
```powershell
.\lazagne.exe all -v
```

## 4) SessionGopher

Инструмент извлекает сохраненных учетных данных PuTTY, WinSCP, FileZilla, SuperPuTTY и RDP

```powershell
Import-Module .\SessionGopher.ps1
 
hostname

Invoke-SessionGopher -Target <hostname>
```

