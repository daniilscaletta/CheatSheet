
## **arjun**

```bash
arjun -u http://target.com/page.php
```

```bash
arjun -u http://target.com/page.php --fast
```

```bash
arjun -u http://target.com/page.php -m POST
```


## **ffuf**

```bash
ffuf -u http://target.com/login -w users.txt -d "username=FUZZ&password=test123" -mr "Welcome"
```

```bash
ffuf -u "http://target.com/endpoint?FUZZ=test_value" -w parameters.txt -fr "error"
```

```bash
ffuf -u http://target.com/api -X POST -d "FUZZ=test" -w params.txt -mc 200
```

```bash
ffuf -u "http://target.com/page?id=FUZZ" -w values.txt -mr "success"
```

