#windows #AD #vulneralabylitiesities 

CVE-2017-0144

#### Возникновения уязвимости
Уязвимость эксплуатирует ошибки _Windows_-реализации протокола _SMBv1_ для удалённого доступа к файлам и другим сетевым ресурсам

Ошибка связана с ошибками в структуре _SMB_-запросов. В рамках уязвимости _EternalBlue_ рассматривается девять ошибок

#### Импакт
Уязвимость также дает возможность исполнения кода с привилегиями _SYSTEM_

#### Уязвимые версии:
Все ОС Windows

#### Эксплойты
[here](https://www.exploit-db.com/exploits/42315)
[here](https://www.exploit-db.com/exploits/43970)

#### Защита
- Заблокировать _TCP_ порт 445 на внешнем периметре
- Отключить _SMBv1_ на всех узлах
```powershell
Disable-WindowsOptionalFeature -Online -FeatureName smb1protocol
```
или
```powershell
Set-SmbServerConfiguration -EnableSMB1Protocol $false
```
- Установить последние обновления безопасности на все узлы с _Windows_
- Узлы, использующие _SMBv1_ выделить в отдельный сегмент с более строгими правилами безопасности

