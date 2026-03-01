#windows #AD #attacks 

`Реинкарнация Pass-the-hash`

При обычной атаке _pth_, мы используем _NTLM_ хеш с целью попасть на другой хост. Это может не всегда срабатывать так, как нам хотелось бы: может быть такое, что целевой хост, который нам нужен использует только _Kerberos_ аутентификацию. Что делать в таком случае, ведь у нас нет ни пароля, ни билетов _Kerberos_, ничего, кроме хеша? Ответ очень прост — использовать _NTLM_ хеш, чтобы получить _TGT_ и потом _TGS_ билет. _Kerberos_ позволяет использовать _NTLM_ хеш, а не пароль при получении билетов (аутентификации) в целях обратной совместимости, однако такие билеты имеют нюанс: шифрование и хеширование
![[Overpass-the-hash.png]]
### Detect
1) При просмотре пакетов AS-REQ увидим, что Mimikatz использует в качестве etype: устаревший ARCFOUR, а не AES256

**Tools:**
##### 1) !**PSexec**

2) Rubeus
```bash
Rubeus asktgt /user:alice /aes256:<key>
```

3) Impacket
```bash
getTGT.py corp.local/alice -aesKey <key>
```

4) Mimikatz
```bash
sekurlsa::pth /aes256:<key>
```

Шумные:
2)  [GoFetch](https://github.com/SkillfactoryCoding/HACKER-LateralMovement-GoFetch),
3) [Angrypuppy](https://github.com/SkillfactoryCoding/HACKER-LateralMovement-ANGRYPUPPY),
4) [DeathStar](https://github.com/SkillfactoryCoding/HACKER-LateralMovement-DeathStar).

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
Mimikatz не сможет читать память.

### 3) Credential Guard

Функция Windows, которая защищает LSASS.
Credential Guard:
- изолирует NT hashes
- использует virtualization‑based security
attacker не может извлечь NT hash.