#windows #AD #attacks 

> Позволяет использовать учетные записи, которые не являются администраторами, но имеют права, позволяющие ими стать

## 1) PowerView
```
# Использование PowerView для анализа путей атаки (BloodHound делает это нагляднее)
Get-DomainObjectAcl -ResolveGUIDs | ? { $_.ActiveDirectoryRights -match "GenericAll|WriteDacl" }
```

## 2) BloodHound


# Protect

1) Мониторить изменения ACL (**Event ID 5136**) и членства в группах (**Event ID 4728/4729**)
2) Сканировать AD через BodHound

