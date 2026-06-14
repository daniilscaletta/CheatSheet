#recon
### Принципы:

 1) Поиск почты любого сотрудника путем перебора маски почты компании
 2) Поиск в открытых утечках
 3) Использование протокола SMTP для пересылки сообьщений

### Понятния SMTP

1) **Почтовый пользовательский агент (MUA)** - визуальная часть программы (Outlook, Thunderbird)
2) **Агент пересылки почты (MTA)** - (Сервер выхода в интернет)
3) 3.1) **Агент отправки почты (MSA)** -  Пограничные части перед MUA
4) 3.2) **Агент доставки почты (MDA)** -  -||-

> Схема транспортировки письма
> MUA → MSA → MTA → Интернет → MTA → MDA → MUA

### Tools:
1) [Email Permutator+](http://metricsparrow.com/toolkit/email-permutator/)
2) **Whois**
	1) [https://dnschecker.org/ip-whois-lookup.php](https://dnschecker.org/ip-whois-lookup.php)
	2) [https://bgp.he.net/](https://www.notion.so/e98d8dce702f4a8e8fc0e677a7935aee)
	3) [https://whois.ru/](https://whois.ru/)
3) [h8mail](https://github.com/khast3x/h8mail)
4) [Infoga](https://github.com/The404Hacking/Infoga)
5) [Maltego](https://www.maltego.com/)
6) DuckDuckGo «[@domainname](https://github.com/domainname "GitHub User: domainname").com» → поиск

#### Верификация почты:
- [https://tools.emailhippo.com/](https://tools.emailhippo.com/)
- [https://verify-email.org/](https://verify-email.org/)
- [https://www.verifyemailaddress.org/](https://www.verifyemailaddress.org/)
- [https://verifalia.com/validate-email](https://verifalia.com/validate-email)
- [https://quickemailverification.com/](https://quickemailverification.com/)
- [https://www.accuwebhosting.com/blog/top-10-bulk-email-list-verification-validation-services-compared/](https://www.accuwebhosting.com/blog/top-10-bulk-email-list-verification-validation-services-compared/)


7) [theHarvester](https://github.com/laramies/theHarvester)


### Использовании `hydra` для генерации имен

> `hydra -L userlist.txt -s 465 smtp.gmail.com smtp`