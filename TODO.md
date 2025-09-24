- **Что изучать?**
	- Широковещательные и мультикаст-пакеты протоколов: mDNS, DHCP, LLMNR, NBT-NS, NDP for IPv6, RTP
	- Протоколы, которые впоследствии могут быть использованы для атак: DTP,STP,CDP, и пр.
- атаки для изучения
	- STP (RSTP, PVSTP, MSTP) spoofing
	- NDP spoofing
	- VLAN hopping
	- SLAAC Attack
	- Hijacking HSRP (VRRP, CARP)
	- ICMP Redirect
	- DHCP spoofing
	- DNS spoofing
	- kerberoas
	
- [bettercap](https://www.bettercap.org/legacy/)(https://github.com/bettercap/bettercap)
- [ettercap](https://github.com/Ettercap/ettercap)
- aircrack-NG
- [yersinia](https://github.com/tomac/yersinia)
- [scapy](https://github.com/secdev/scapy/)

- [pivoting Practic](https://hackware.ru/?p=9016#10)
- DNS tunneling, практика, защита


- Dynamic routing protocol spoofing (BGP)
- RIPv2 Routing Table Poisoning
- OSPF Routing Table Poisoning
- EIGRP Routing Table Poisoning

**Cobalt Strike**
стейджер `windows/meterpreter_reverse_https` (нагрузка без стейджера)


вешать домен
вешать флару
рега tg



LINUX:
lvm2
chattr
useradd/adduser
lynis


СВОЙ OpenVPN (https://habr.com/ru/articles/233971/, https://apps.skillfactory.ru/learning/course/course-v1:SKILLFACTORY+hack_pentest+2020/block-v1:SKILLFACTORY+hack_pentest+2020+type@sequential+block@99b059f96242484b869014a9c21cad6b/block-v1:SKILLFACTORY+hack_pentest+2020+type@vertical+block@93903eaba66b434099e7fe1158ea9bef)


ВСЕ ТЕМЫ ПО НОВОЙ В GPT



«_Best Practies_», например, [CIS Benchmarks](https://www.cisecurity.org/cis-benchmarks/).
nirSoft - сбор Windows Tools, trojan, ...
Шифрование сообщений почты





webAuthn
	1) метод аутентификации service Worker / замыкания
	2) trusted types как защита от XSS 
	3) Как настроить регулярное обновление любой фичи: библы, фреймворка
	4) back2back передача данных






написать скрипты на Python
1) [x] **Port Scanner (асинхронный)** — быстрый TCP/UDP сканер на `asyncio/socket`
2) [x] **HTTP Header Analyzer** — проверка security-заголовков (CSP, HSTS, X-Frame-Options и т.д.).
3) [x] **Subdomain Bruteforcer** — перебор поддоменов через словарь и DNS-запросы.
4) [x] **Directory/File Bruteforcer (Web Fuzzer)** — поиск скрытых директорий/файлов на вебе.
5) [ ] **Login Brute/Password Spray Script** — перебор логинов/паролей (с прокси и ротацией User-Agent).
6) [ ] **XSS Payload Injector** — массовая проверка параметров сайта на XSS.
7) [ ] **Simple Exploit Template** — каркас для написания эксплойтов (запрос + payload + проверка результата).
8) [ ] **Redis Misconfig Checker** — поиск открытых Redis, проверка версии и дамп ключей.
9) [ ] **SMB/FTP Anonymous Login Checker** — тест анонимного входа в общие сервисы.
10) [ ] **ARP Spoofer / MITM Sniffer** — ARP-spoof атака и перехват трафика (`scapy`).






////////////////////TOR////////////////////////
Цепочка прокси прям из браузера
https://проксиА: nopm/https://проксиБ:nopmlhttps:/lwww.xakep.ru

Более безопасно 
VPN Через Tor (*) (AirVPN и BolehVPN)
Tor через VPN

Использовать DuckDuckGo
HTTPS
Англ яз

Настройка выходных узлов torrc (Страна)
ExitNodes {DE)
StrictExitNodes 

Через что не должен проходить трафик
ExcludeNodes {ru}, {ua}, {Ьу)

Мы НЕ выходной узел!
ExitPolicy reject *:* # no exits allowed
ExitPolicy rejectб *:* # no exits allowed


Рекомендации
1) Sim без привязки к паспарту 
2) Виртуалка
3) VPN + Tor
4) Использовать анонимный ящик  tuta.io 
5) Мессенджеры без привязки к номеру
6) Разные пароли
7) Оплата только через Bitcoin

////////////////////////////////////////////






BOOKS:

1) Архитекрутра компьютера - Танненбаум
2) Сети - Олифер | Танненбаум
3) Операционные системы - Танненбаум | Unix и Linux Руководство Сис Админа

4) Пенетест - 
	1) Этичный хакинг
	2) Хакинг на примерах
	3) Хакинг на C++
 