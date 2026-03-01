#tool #windows #recon 

Это аналитический и графический инструмент для поиска оптимального пути для продвижения внутри домена

BloodHound ничего не эксплуатирует, он лишь показывает доступные права, которые настроены неверно

### Состав 
#### 1) SharpHound
Специальный агент, который запускается внутри домена и читает все данные о домене: WinRM, SMB, LDAP, RPC
#### 2) Neo4j
Графовая БД. Хранит все данные, собранные с SharpHound
#### 3) Bloodhound GUI
Приложение визуализирующее граф

### Эксплуатация

#### 1) Сбор данный в формате .zip, .json

- ##### Bloodhound-python
Login + pass
```bash
bloodhound-python -u 'amaslova' -p 'NeverGiv3up' -ns 192.168.2.4 -d codeby.cdb -c all --zip
```

Kerberos
```bash
bloodhound-python -k -u 'amaslova' -ns 192.168.2.4 -d codeby.cdb -c all --zip
```

NTLM-hash
```bash
bloodhound-python -u 'amaslova' -H <domain> -ns 192.168.2.4 -d codeby.cdb -c all --zip
```

- ##### Sharphound.exe
```bash
SharpHound.exe -d <domain> -dc <DC> -c All -o C:\Temp\BH
```

- ##### PowerShell
```powershell
Import-Module .\SharpHound.ps1
Invoke-BloodHound -CollectionMethod All
```

#### 2) Развертывание 

```bash
git clone https://github.com/SpecterOps/BloodHound.git
cd BloodHound
docker-compose up -d
```