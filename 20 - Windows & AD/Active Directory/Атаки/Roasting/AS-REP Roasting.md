#AD #windows #privillage #attacks #auth 

> Атака _AS-REP roasting_ нацелена на пользователей в домене, у которых отсутствует опция «требовать предварительной аутентификации _Kerberos_»


### Kerberos аутентификация (c pre-auth):

1. Пользователь при аутентификации прикладывает в _AS_REQ id_ клиента, _timestamp_ и _id_ сервера и отсылает в сторону _KDC_ запрос.
2. _KDC_ отвечает _KRB_error_, требуя при этом прислать «нормальный _AS_REQ_», в котором используется пароль пользователя (требует предварительной аутентификации).
3. Пользователь шифрует с помощью своего пароля _timestamp_ и отправляет _AS-REQ_ в сторону _KDC_.
4. _KDC_ пытается расшифровать с помощью пользовательского пароля. Если получается, то с помощью своего ключа (_krbtgt_) подписывает билет _TGT_ и в него прикладывает так же зашифрованную часть _AS_REP_ с помощью ключа клиента.

### Kerberos аутентификация (без pre-auth):

1. Пользователь при аутентификации прикладывает в _AS_REQ id_ клиента, _timestamp_ и _id_ сервера и отсылает в сторону _KDC_ запрос.
2. _KDC_ с помощью своего ключа (_krbtgt_) подписывает билет _TGT_ и в него прикладывает так же зашифрованную часть _AS_REP_ с помощью ключа клиента (_KDC_ же знает все пароли, правильно?).

В случае с отсутствием pre-auth _KDC_ не требует зашифрованный _timestamp_ с помощью пользовательского пароля. Т.е. можно получить _TGT_ без пароля. Имея такой билет на руках, можно попытаться сбрутить пароль и расшифровать билет, получив таким образом пароль пользователя в открытом виде, сбрутив его оффлайн

НО, по умолчанию все учетки по умолчанию имеют pre-auth

ОДНАКО, если у учетки есть права _GenericWrite/GenericAll_, то можно отключить требование предварительной аутентификации _Kerberos_

Поиск уязвимых пользователей
```powershell
Get-ADUser -Filter {DoesNotRequirePreAuth -eq $true} -Properties DoesNotRequirePreAuth
```
### Инструменты:

1)  [[[Rubeus]]](https://github.com/SkillfactoryCoding/HACKER-OS-Rubeus) (модуль [asreproast](https://github.com/SkillfactoryCoding/HACKER-OS-Rubeus/blob/master/Rubeus/Commands/Asreproast.cs)) — получение хеша пользователя.
```powershell
.\Rubeus.exe asreproast /outfile:hashes.txt
```
2)  [[[Impacket]]](https://github.com/SkillfactoryCoding/HACKER-OS-impacket) ([GetNPUsers.py](https://github.com/SkillfactoryCoding/HACKER-OS-getnpusers.py/blob/main/getnpusers.py)) — поиск пользователей без предварительной аутентификации.
3)  [Hashcat](https://hashcat.net/hashcat/) — поможет сбрутить хеш.
4)  [John The Ripper](https://hackware.ru/?p=13396) — поможет сбрутить хеш (устаревший инструмент, сейчас чаще используют _hashcat_).