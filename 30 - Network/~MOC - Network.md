# Network — MOC

> Сетевые атаки: MITM, VLAN, Wi-Fi, атаки на протоколы (ARP, DHCP, DNS, IPv6), инструменты разведки.

## Оглавление
- [[#MITM-атаки]]
- [[#VLAN-атаки]]
- [[#Беспроводные сети (Wi-Fi)]]
- [[#Протоколы и сервисы]]
- [[#Инструменты разведки]]
- [[#Сетевая эксплуатация]]

---

## MITM-атаки

- [[DHCPv6 Spoofing ; Rogue RA]] — спуфинг DHCPv6 и Rogue Router Advertisement
- [[LLMNR ; NBT-NS ; mDNS Spoofing]] — отравление LLMNR/NBT-NS/mDNS

**Инструменты MITM:**
- [[Bettercap 2.0]] — многофункциональный MITM-фреймворк
- [[Ettercap]] — классический инструмент MITM
- [[Intercepter-ng]] — MITM-инструмент с GUI
- [[Pretender]] — автоматизированный MITM в Windows-сетях
- [[mitm6]] — IPv6 MITM-атака
- [[mitmproxy]] — перехват и анализ HTTP/HTTPS трафика

## VLAN-атаки

- [[VLAN]] — основы VLAN
- [[VLAN Hopping]] — атака переключения VLAN
- [[Двойное теггирование (Double tagging)]] — двойное тегирование 802.1Q

## Беспроводные сети (Wi-Fi)

**Инструменты aircrack-ng suite:**
- [[1) airmon-ng]] — перевод адаптера в режим мониторинга
- [[2) airodump-ng]] — захват пакетов Wi-Fi
- [[3) aireplay-ng]] — инъекция пакетов
- [[4) aircrack-ng]] — взлом ключей WEP/WPA
- [[5) airbase-ng]] — создание точки доступа

**Атаки на Wi-Fi:**
- [[WEP]] — атаки на устаревший протокол WEP
- [[Атаки с перехватом (WPA, WPA2)]] — захват handshake и взлом
- [[Downgrade атаки]] — понижение версии протокола
- [[Фишинговые атаки]] — Evil Twin и фишинг Wi-Fi
- [[Эксплуатация WPS]] — атаки на WPS (PIN, Pixie Dust)

**Безопасность Wi-Fi:**
- [[PMF]] — Protected Management Frames
- [[Wi-Fi 7]] — особенности и безопасность Wi-Fi 7
- [[WPA2]] — протокол WPA2
- [[WPA3]] — протокол WPA3

**Прочие инструменты:**
- [[RouterSploit]] — эксплуатация роутеров

## Протоколы и сервисы

**ARP:**
- [[ARP-Spoofing]] — подмена ARP-записей

**DHCP:**
- [[DHCP]] — основы протокола DHCP
- [[DHCP starvation]] — истощение пула адресов DHCP
- [[Rogue DHCP]] — мошеннический DHCP-сервер

**DNS:**
- [[DNS]] — основы DNS
- [[DNS Cache poisoning (DNS-spoofing)]] — отравление кэша DNS
- [[DNS flooding]] — флуд DNS-запросами
- [[Garbage DNS]] — мусорные DNS-запросы
- [[Rogue DNS Server]] — мошеннический DNS-сервер

**IPv6:**
- [[IP-spoofing]] — подмена IP-адреса (IPv6)

## Инструменты разведки

- [[NMAP]] — сетевой сканер портов и сервисов

## Сетевая эксплуатация

- [[Атаки на сетевые сервисы]] — эксплуатация сетевых сервисов
