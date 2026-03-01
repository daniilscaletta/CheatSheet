#tool #windows #kerberos

Мощный инструмент для атак на AD через Kerberos
Ключевая особенность - работает через Kerberos, а не LDAP/SMB

> Kerbrute **не ломает Kerberos**, он ломает **людей и пароли**.

Использует **AS-REQ / AS-REP**, поэтому почти не вызывает триггеры

### Использование

1) **passwordspray**
Применение метода брутфорса для нахождение валидной учетной записи к паролю
```bash
kerbrute passwordspray -d <domain> --dc <ip> users.txt "<pass>" 
```

2) **bruteforce**
Подбор пароля к одному пользователя
```bash
kerbrute bruteforce <username> -d <domain> --dc <ip> passwords.txt 
```

3) **userenum**
Перебор существующих юзеров
```bash
kerbrute userenum users.txt -d <domain> --dc <ip>
```