
## **ffuf**

```bash
ffuf -u "http://target.com/FUZZ" -w /Users/scaletta/fapfolder/CTF/SecLists/Fuzzing/LFI/LFI-Jhaddix.txt
```

```bash
ffuf -u "http://target.com/FUZZ" -w /Users/scaletta/fapfolder/CTF/SecLists/Fuzzing/LFI/LFI-Jhaddix.txt -mc 200,301 -fs 0
```

```bash
ffuf -u "http://target.com/?FUZZ=test" -w /Users/scaletta/fapfolder/CTF/SecListsFuzzing/LFI/LFI-Jhaddix.txt -mr "error"
```


