#tool #mssql #windows 

Удобный клиент для MS SQL БД

### Использование

```bash
impacket-mssqlclient user:pass@ip
```

Если ошибка, попробовать для Windows

```bash
impacket-mssqlclient user:pass@ip -windows-auth
```




Далее включаем работу командной оболочки
```mssql
SQL> enable_xp_cmdshell
```

После чего проверяем свои привилегии
```powershell
SQL> xp_cmdshell whoami /priv
```

