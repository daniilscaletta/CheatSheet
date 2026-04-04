#wifi #tool
### поддельная точка доступа (Rogue AP)

Поднимает **фейковую Wi-Fi точку доступа**. Используется для:

- Evil Twin
- MITM
- перехвата handshakes
- старых атак на клиентов без PMF

Работает через инжект кадров, **не через полноценный hostapd** → нестабильный, но быстрый.

---
#### Типичные сценарии

- Клиенты автоматически подключаются к «знакомому» ESSID
- Захват WPA/WPA2 handshake
- Примитивный downgrade / ловля клиентов

---
#### Примеры команд

Минимальный Rogue AP:
```bash
airbase-ng -e FreeWiFi wlan0mon
```

Поддельная точка с MAC как у жертвы:
```bash
airbase-ng -e TargetWiFi -a 40:AE:30:3C:6D:64 wlan0mon
```

Фиксация канала:
```bash
airbase-ng -c 6 -e TargetWiFi wlan0mon
```

---
#### Что появляется после запуска

- интерфейс `at0`
- дальше руками:
    - `ifconfig at0 up`
    - `dhcpd`
    - `iptables`
    - `ip_forward`

airbase-ng — это **конструктор “собери MITM сам”**.
