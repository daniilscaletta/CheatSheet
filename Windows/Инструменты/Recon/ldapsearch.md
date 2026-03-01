#tool #AD #recon #windows #ldap 

> Инструмент для чтения данных из LDAP AD

> Сырой и текстовый BloodHound
# Эксплуатация 

Вытаскивает всю информацию, если есть анонимный доступ
```bash
ldapsearch -x -H ldap://<ip> -b "dc=codeby,dc=cdb" "(objectClass=*)"
```

- objectClass - менять в зависимости от того, что нам необходимо

