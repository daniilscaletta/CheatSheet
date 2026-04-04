#windows #AD #vulneralabylitiesities

CVE-2021-26855, CVE-2021-26857, CVE-2021-26858, CVE-2021-27065

### Из-за чего возникает?

Проблема в архитектуре Exchange. Сервер состоит из «фасада» (Frontend), который принимает запросы из интернета, и «бэкенда» (Backend).

- **Баг:** Хакер мог отправить специально сформированный HTTP-запрос на Frontend, который заставлял сервер думать, что запрос уже прошел проверку подлинности.
- Это называется **SSRF (Server-Side Request Forgery)**. В итоге анонимный пользователь получал права администратора на уровне веб-сервисов Exchange.
#### Импакт
- PrivEsc
- SSRF
- Shell

#### Защита
Установить последние обновления безопасности для серверов _MS Exchange_

#### Обнаружение уязы
- [Safety Scanner](https://docs.microsoft.com/en-us/windows/security/threat-protection/intelligence/safety-scanner-download)
- [Test-ProxyLogon](https://github.com/SkillfactoryCoding/HACKER-LateralMovement-CSS-Exchange/tree/main/Security)
