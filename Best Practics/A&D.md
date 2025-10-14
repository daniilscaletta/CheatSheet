
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

# **Scout**

