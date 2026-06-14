#windows #AD #attacks 

> Позволяет использовать учетные записи, которые не являются администраторами, но имеют права, позволяющие фактически ими стать

## Оглавление
- [[#1) PowerView]]
  - [[#Использование PowerView для анализа путей атаки (BloodHound делает это нагляднее)]]
- [[#2) BloodHound]]

---

## 1) PowerView

### Использование PowerView для анализа путей атаки (BloodHound делает это нагляднее)
```
Get-DomainObjectAcl -ResolveGUIDs | ? { $_.ActiveDirectoryRights -match "GenericAll|WriteDacl" }
```

## 2) BloodHound

Вбивашь в поиск `Domain Admins` и выбираешь функцию 
`Find Shortest Paths to Domain Admins`. [[BloodHound]] покажет цепочку: 
`User X` -> `GenericWrite` -> `Group Y` -> `WriteDacl` -> `Domain Admin`

Protect

1) Мониторить изменения ACL (**Event ID 5136**) и членства в группах (**Event ID 4728/4729**)
2) Сканировать AD через BloodHound

