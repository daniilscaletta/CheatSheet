

## **dirsearch**

```bash
dirsearch -u http://target.com -e php,html,js,txt,bak,zip,json 
```

```bash
dirsearch -u http://target.com -e php,html,js,txt,bak,zip,json -w /usr/share/wordlists/dirb/common.txt
```

```bash
dirsearch -u http://target.com -e php,html,js,txt,bak,zip,json -r -R 3  
# рекурсия глубиной 3

## Оглавление
- [[#**dirsearch**]]
- [[#**Gobuster**]]

---

```

```bash
dirsearch -u http://target.com -e php,html,js,txt,bak,zip,json --header "Cookie: session=123"
```



## **Gobuster**

```bash
gobuster dir -u http://target.com -w /usr/share/wordlists/dirb/common.txt
```

```bash
gobuster dir -u http://target.com -w /usr/share/wordlists/dirb/common.txt 
-x php,html,txt
```

```bash
gobuster dir -u http://target.com -w wordlist.txt -H "Authorization: Bearer token123" -H "X-Custom-Header: value"
```