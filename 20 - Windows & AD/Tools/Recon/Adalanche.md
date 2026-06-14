#tool #AD #recon #acl #ldap #blueteam #redteam

**Adalanche** — **визуализатор атак на Active Directory**. Строит граф зависимостей и прав в AD, показывает — кто на самом деле может стать Domain Admin, используя цепочки ACL, делегирование и другие мисконфигурации.

Отвечает на вопрос: _«Кто реально является Domain Admin через цепочку прав?»_

## Как работает

1. Подключается к AD по LDAP и собирает данные: пользователи, группы, GPO, ACL, SPN, делегирование, ADCS
2. Строит граф зависимостей между объектами (рёбра = права/отношения)
3. Запускает веб-интерфейс для интерактивного исследования графа
4. Поддерживает Adalanche Query Language (AQL) для сложных запросов

## Что анализирует

- ACL и ownership объектов AD
- Kerberoastable и unconstrained delegation аккаунты
- Уязвимости ADCS (ESC1-ESC8 и др.)
- Права GPO и OU
- Windows-машины (domain joined)
- VMware vSphere (в платной версии)

## Эксплуатация

### Установка

```bash
# Скачать бинарь со страницы релизов

## Оглавление
- [[#Как работает]]
- [[#Что анализирует]]
- [[#Эксплуатация]]
  - [[#Установка]]
  - [[#1. Сбор данных из AD]]
  - [[#2. Анализ и запуск веб-интерфейса]]
  - [[#3. Запросы AQL (примеры)]]
- [[#Практический кейс]]
- [[#Важные замечания]]

---

# https://github.com/lkarlslund/Adalanche/releases

# Или собрать из исходников
git clone https://github.com/lkarlslund/Adalanche
cd Adalanche && go build ./cmd/adalanche
```

### 1. Сбор данных из AD

```bash
# Аутентификация с кредами (из любой машины)
./adalanche collect activedirectory \
  --domain contoso.local \
  --username user@contoso.local \
  --password 'P@ssw0rd'

# Из доменной машины (текущий пользователь)
./adalanche collect activedirectory --domain contoso.local

# Сбор данных с Windows-машин
./adalanche collect localmachine
```

Данные сохраняются в папку `data/` в формате `.gcache`.

### 2. Анализ и запуск веб-интерфейса

```bash
./adalanche analyze
```

Открывается браузер с интерактивным графом. По умолчанию: `http://localhost:8080`

### 3. Запросы AQL (примеры)

```
# Кто может сбросить пароль Domain Admin?
(u:User {admincount:1})<-[ResetPassword*1..]-()

# Все пути к Domain Admins
()-[*1..5]->(g:Group {name:"Domain Admins"})

# Kerberoastable аккаунты с путём к DA
(u:User {hasspn:true})-[*1..4]->(g:Group {name:"Domain Admins"})
```

## Практический кейс

Запустить в начале внутреннего пентеста — даёт мгновенный обзор всех мисконфигураций и кратчайших путей к Domain Admin без ручного анализа ACL.

## Важные замечания

- Открытая версия — только AD + Windows-машины; платная версия (NetSection) добавляет vSphere, CyberArk, отчёты
- Альтернативы: [[BloodHound]] (более распространён), PingCastle (compliance-ориентирован)
- Требует права на чтение AD — минимум обычный доменный пользователь
