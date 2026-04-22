#forwarding #ssh #tunneling 

> `Sshuttle` обеспечивает автоматизированную настройку туннелей <span style="background:#fff88f">через SSH</span>, без дополнительных ручных настроек и без `proxychains`

```bash
sudo apt-get install sshuttle

sudo sshuttle -r ubuntu@10.129.202.64 172.16.5.0/23 -v 
```

Обеспечивает доступ во внетреннюю сеть `172.16.5.0/23` через промежуточный `ubuntu@10.129.202.64`
