#protocol #cyberkillchain #recon #dns

Как происходит резолвинг:
![Flowchart showing two main sections: User Database and Data Collection. Includes steps like 'Check User', 'Send to Source Database', 'Store Data', and 'Send to UI System'.|700](https://mermaid.ink/svg/pako:eNptkk1uwjAQha8y8rpcIItWkAAtUNQmlSrksDDxlEQQT-QfJIS4ex2nNG1arzx-n5-ex3NhBUlkEdtr0ZSwSnMFfhm36w425DTEVDfOou60do15XGJxMBCLosQtjEb3MLk8vcCMnJIP156ceA3WFIiYZ6ikgWSdwatDfQZLkKKh4wn1dnBngyZceuQxKYWFNS39jjtTWfyCvdsgb2t9c-wN4-CU_A7dy8mPjFOeYuG0qU4IK6KDa4bgLdjck9ZpZcC_20e7dWmYbRroGU-JLKxFjZCh7h88C_KCv62Sf9RFUJd87GxJurLCtsH-cssuUlfMu8blit2xGnUtKul_-NKKObMl1pizyG-l0Iec5erqOeEsZWdVsMhqh3dMk9uXLPoQR-Mr10hhMamE73L9fYqysqSfuwEKc3T9BOe0sj4)

1. `Your Computer Asks for Directions (DNS Query)`Когда вы вводите доменное имя, ваш компьютер сначала проверяет свою память (кэш), чтобы убедиться, что он помнит IP-адрес с предыдущего посещения. Если нет, он обращается к DNS-серверу, обычно предоставляемому вашим интернет-провайдером (ISP).
2. `The DNS Resolver Checks its Map (Recursive Lookup)`У резолвера также есть кэш, и если он не находит IP-адрес там, он начинает свой путь по иерархии DNS. Сначала он обращается к корневому серверу имен, который подобен библиотекарю интернета.
3. `Root Name Server Points the Way`Корневой сервер не знает точного адреса, но знает, кто его знает — сервер имен верхнего уровня (TLD), отвечающий за окончание домена (например, .com, .org). Он указывает резолверу правильное направление.
4. `TLD Name Server Narrows It Down`Сервер имен верхнего уровня (TLD) подобен региональной карте. Он знает, какой авторитетный сервер имен отвечает за конкретный домен, который вы ищете (например, `example.com`) и отправляет туда резолвер.
5. `Authoritative Name Server Delivers the Address`Авторитетный сервер имен — это конечная точка. Это как почтовый адрес нужного вам веб-сайта. Он хранит правильный IP-адрес и отправляет его обратно в резолвер.
6. `The DNS Resolver Returns the Information`: Резолвер получает IP-адрес и передает его на ваш компьютер. Он также запоминает его на некоторое время (кэширует) на случай, если вы захотите снова посетить веб-сайт в ближайшее время.
7. `Your Computer Connects`Теперь, когда ваш компьютер знает IP-адрес, он может напрямую подключиться к веб-серверу, на котором размещен веб-сайт, и вы можете начать просмотр.

DNS-записи:

A – используется для указания доменного имени, например, testdomain.com, на IP-адрес его хост-сервера;  
MX –  указывает почтовый сервер, ответственный за прием электронных писем от имени доменного имени 
NS – предназначены для идентификации DNS-серверов, ответственных за домен;  
SRV – записи для выделения службы, размещенной на определенных серверах;  
PTR – обратный поиск DNS: с помощью IP вы можете получить связанный с ним домен;  
SOA – начало записи: это информация о зоне DNS и других записях DNS;  
TXT - можно положить абсолютно любую информацию, часто используется для обеспечения доп уровня безопасности;
CNAME – сопоставляет целевое доменное имя с другим доменным именем.