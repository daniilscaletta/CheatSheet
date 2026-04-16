#honeypot #defense #monitoring #GPO
# Суть 

Мы создаем GPO, привлекательную для атакующего, но которую админы никогда не трогают и настраиваем скрипт для анализа ее измненения
# Скрипт Powershell

```powershell
$TimeSpan = (Get-Date) - (New-TimeSpan -Minutes 15)
$Logs = Get-WinEvent -FilterHashtable @{LogName='Security';id=5136;StartTime=$TimeSpan} -ErrorAction SilentlyContinue |`
Where-Object {$_.Properties[8].Value -match "CN={73C66DBB-81DA-44D8-BDEF-20BA2C27056D},CN=POLICIES,CN=SYSTEM,DC=EAGLE,DC=LOCAL"}


if($Logs){
    $emailBody = "Honeypot GPO '73C66DBB-81DA-44D8-BDEF-20BA2C27056D' was modified`r`n"
    $disabledUsers = @()
    ForEach($log in $logs){
        If(((Get-ADUser -identity $log.Properties[3].Value).Enabled -eq $true) -and ($log.Properties[3].Value -notin $disabledUsers)){
            Disable-ADAccount -Identity $log.Properties[3].Value
            $emailBody = $emailBody + "Disabled user " + $log.Properties[3].Value + "`r`n"
            $disabledUsers += $log.Properties[3].Value
        }
    }
    # Send an alert via email - complete the command below
    # Send-MailMessage
    $emailBody
}
```

- **Задает временное окно:** Вычисляет интервал за последние **15 минут**, чтобы проверять только свежие события в логах.

- **Ищет событие 5136:** Опрашивает журнал «Security» на предмет изменения объектов Active Directory (Event ID 5136).

- **Фильтрует по GUID:** Оставляет только те записи, которые относятся к конкретной **GPO-ловушке** (по её уникальному ID).

- **Идентифицирует атакующего:** Извлекает из лога имя пользователя (поле `Properties[3]`), который внес изменения.

- **Проверяет статус:** Убеждается через `Get-ADUser`, что учетная запись нарушителя все еще активна.

- **Блокирует учетку:** Немедленно выполняет `Disable-ADAccount` для аккаунта, совершившего изменение.

- **Формирует отчет:** Собирает данные о заблокированном пользователе в текст письма для администратора.