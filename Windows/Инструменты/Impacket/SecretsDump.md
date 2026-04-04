#tool #windows 

Инструмент из пакета Impacket, который позволяет **получить хэши паролей и секреты Windows** (SAM/LSA/NTDS) **удалённо**, без запуска агента на целевой машине (в большинстве сценариев).

Это мощный инструмент для **кражи учётных данных** на Windows/AD.

### Условия для применения

1) Наличие каких-либо привилегий
- Права Локального администратора
- Права **Replicating Directory Changes**

2) Любой доступ к машине
- SMB
- RPC

### Импакт

1) **SAM хэши локальных пользователей** (LM/NTLM)
2) **Cached domain logons**
3) **LSA secrets** (секреты системы, пароли сервисов, DPAPI ключи)
4) **Domain credentials** из NTDS.dit

### Использование

```bash
impacket-secretsdump <domain>/<user>:<pass>@<IP> -user-status
```

- Извлечение только из NTDS.dit, смотреть историю изменения
```bash
impacket-secretsdump -outputfile <file_hashes> -just-dc <domain>/<user>@<ip> 
-history -user-status
```

