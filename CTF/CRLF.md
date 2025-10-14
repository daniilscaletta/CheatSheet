```bash
crlfuzz -u "https://example.com/search?q=test"
```

```bash
crlfuzz -u "https://vulnerable.site/search?query=fuzz"
```

```bash
crlfuzz -u "https://example.com" -x http://127.0.0.1:8080 # proxy
```
