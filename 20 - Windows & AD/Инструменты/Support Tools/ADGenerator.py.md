#tool #AD #windows 

Тулза для генерации имен пользователей домена для проведения атаки на перебор, например, [[AS-REP Roasting]]

Необходимо подготовить файл с именами пользователя в формате `csv`:
1) Name,Surname
2) Name,Surname
3) Name,Surname

Если у нас есть просто файл в формате `txt`:
1) Name Surname
2) Name Surname
3) Name Surname

Можно воспользоваться командой 
```bash
cat users.txt | sed "s/\s/,/" > users_csv.txt
```

Далее юзаем уже скрипт [ADGenerator.py](https://github.com/w0Tx/generate-ad-username/blob/main/ADGenerator.py)
```bash
python3 ADGenerator.py users_csv.txt > possible_usernames.txt
```