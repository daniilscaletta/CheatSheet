#tool #AD #wmi #windows

`wmiexec` — это инструмент из **[[Impacket]]**, который даёт **удалённое выполнение команд на Windows через WMI (Windows Management Instrumentation)**.

> **Удалённый shell без записи файла на диск и без сервиса.**

Он работает **без WinRM**, без RDP и без загрузки бинарей на цель.

> **ЛУЧШЕ, ЧЕМ PSEXEC**


## Эксплуатация 

```bash
impacket-wmiexec <DOMAIN>/<user>:'<pass>'@<ip>
```

PtH
```bash
impacket-wmiexec <DOMAIN>/<user>@<ip> -hashes :NTLM_HASH
```

kerberos
```bash
impacket-wmiexec -k -no-pass <DOMAIN>/<user>@<ip>
```