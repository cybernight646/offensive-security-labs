Ransomware & Decryptor (Red Team Research Project)
Overview

This repository contains two complementary Python scripts designed strictly for red team research, malware analysis, and defensive learning:

Ransomware Simulation Script – demonstrates file encryption behavior using symmetric cryptography.

Decryptor Utility – restores encrypted files after key recovery to validate incident‑response and recovery workflows.

The project exists to help researchers and defenders understand how ransomware operates technically, how encryption impacts systems, and how recovery mechanisms function in controlled environments.

This repository is intentionally maintained as private and is not intended for public distribution or real‑world deployment.

Intended Use Environment

Execution is limited to controlled lab environments

Systems must be owned by or explicitly authorized for testing

Only non‑sensitive, test files should be used

The code must never be executed on production or third‑party systems

Operating System

Microsoft Windows only

The project relies on Windows‑specific filesystem behavior and APIs

Project Components
1. Ransomware Simulation Script
Purpose

The ransomware script demonstrates:

Symmetric file encryption at scale

Concurrent file processing behavior

Ransom note creation and user notification

Key‑handling separation from decryption logic

This script is educational by design and prioritizes behavioral clarity over stealth or persistence.

High‑Level Behavior

Generates a Fernet symmetric encryption key
Encrypts files matching predefined extensions
Writes a ransom note to the filesystem
Protects the symmetric key using asymmetric cryptography
Leaves recovery intentionally dependent on key restoration

***The script does not***:
Exfiltrate data
Communicate with command‑and‑control infrastructure
Attempt lateral movement
Perform evasion or obfuscation

2. Decryptor Utility
Purpose

The decryptor is a standalone recovery tool used to demonstrate:

Post‑incident file restoration

Key‑based decryption workflows

Separation of encryption and recovery logic

Defensive validation and incident response simulation

High‑Level Behavior

Monitors for a file named PUT_ME_ON_DESKTOP.txt

Reads a Fernet symmetric key from that file

Decrypts previously encrypted files

Processes files concurrently

Terminates automatically after successful decryption

The decryptor does not generate keys, modify the system state beyond file restoration, or communicate externally.

Execution Scope

File operations are scoped to a researcher‑defined test directory

Only explicitly listed file extensions are processed

System binaries and OS‑critical paths are out of scope

System‑wide execution is explicitly discouraged

Researchers are expected to restrict execution to sample data created for testing purposes.

Cryptographic Design

This project demonstrates a hybrid cryptographic model commonly observed in real‑world ransomware:

Symmetric encryption (Fernet) for file operations

Asymmetric cryptography (RSA) for key protection

Assumptions

An RSA public key is expected to exist in the execution directory

Private key handling and recovery workflows are intentionally excluded

Proper key lifecycle management is assumed in a research environment

No cryptographic hardening or evasion techniques are implemented.

Python Runtime Requirements

Python 3.x

Required Dependencies

cryptography

pycryptodome

pywin32

requests

concurrent.futures (standard library)

Dependency installation and environment isolation are assumed to be handled by the researcher.

Design Constraints

The code is not production‑ready

No obfuscation or anti‑analysis techniques are used

The implementation prioritizes:

Readability

Traceability

Defensive understanding

This is a learning and research artifact, not an operational tool.

Ethical and Legal Disclaimer

This project is provided strictly for educational, research, and defensive purposes.

Any use outside of authorized lab environments is unethical and potentially illegal.
I assumes no responsibility for misuse or unauthorized execution.
Repository Status
Maintained as private
Not intended for redistribution
Shared only in controlled professional or academic contexts


QUICK DEMO.
we will select a particular folder to encrypt everything inside, From images,txt,

-Create a folder name "TEST_ENCRYPTION"  ON the Desktop

-Put or copy all types of files images,pdfs,text etc. into the folder

-change the folder path to thisself.sysRoot = os.path.join(os.path.expanduser("~"), "Desktop", "test_encryption")

-Compile and run the application but the simplest way is to run it from your idle.I will be using sublime for now

-After running check the folder to see that all files are encrypted.And also  your backgroung will change and there will be a note on the desktop.

-Now we can decrypt the files by runing the decrypter.py .NB:The decryptor.py assumes there is put_me_on_desktop.txt(which contains the private AES key).It reads the key and uses it to decrypt the fernet key and decrypts the entire files.

A QUICK DIAGRAM IS SHOWN BELOW.
![Image ALT](https://github.com/cybernight646/offensive-security-labs/blob/d33d86ba8173221afbb21b36e6ef439809417f95/Ransomware_practical/Screenshot%20(104).png)



