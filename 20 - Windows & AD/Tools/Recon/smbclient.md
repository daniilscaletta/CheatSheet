#tool #windows #AD

Инструмент из пакета Samba, необходим для **доступа к SMB-шарам, перечисления ресурсов и скачивания/загрузки файлов**.
### Условия для применения
1. SMB доступ
```bash
445/tcp open  microsoft-ds 
139/tcp open  netbios-ssn
```

### Использование

```bash
smbclient -L //<ip>
```

```bash
smbclient -L //<ip> -U user
```

### Эксплуатация

1) Просмотр доступных шар
```bash
smbclient -L //<ip> -U user
```

2) Подключение к шаре
```bash
smbclient //<ip>/<share> -U <domain>\\<user>
```

3) Взаимодействие с файлами как с ftp 

```bash
smbclient //<ip>/<Открытая Шара> 

smb: \> recurse on       // Автоматически рекурсивно скачивать папки 
smb: \> prompt off       // Отключение подтверждения
smb: \> mget *           // Скачать все
```