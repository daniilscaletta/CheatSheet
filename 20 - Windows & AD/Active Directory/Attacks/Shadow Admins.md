#windows #AD #attacks 

> Позволяет использовать учетные записи, которые не являются администраторами, но имеют права, позволяющие фактически ими стать

## 1) PowerView

```
Get-DomainObjectAcl -ResolveGUIDs | ? { $_.ActiveDirectoryRights -match "GenericAll|WriteDacl" }
```

