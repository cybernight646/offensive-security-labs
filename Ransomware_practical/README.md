## Ransomware & Decryptor (Red Team Research Project)
### Overview

This repository contains two complementary Python scripts designed strictly for red team research, malware analysis, and defensive learning:

Ransomware Simulation Script – demonstrates file encryption behavior using symmetric cryptography.

Decryptor Utility – restores encrypted files after key recovery to validate incident‑response and recovery workflows.

The project exists to help researchers and defenders understand how ransomware operates technically, how encryption impacts systems, and how recovery mechanisms function in controlled environments.

This repository is intentionally maintained as private and is not intended for public distribution or real‑world deployment.

Intended Use Environment

Execution is limited to controlled lab environments

Systems must be owned by or explicitly authorized for testing

Only non‑sensitive, test files should be used

## The code must never be executed on production or third‑party systems

Operating System

Microsoft Windows only

The project relies on Windows‑specific filesystem behavior and APIs

 ### Project Components
1. Ransomware Simulation Script
Purpose

The ransomware script demonstrates:

Symmetric file encryption at scale

Concurrent file processing behavior

Ransom note creation and user notification

Key‑handling separation from decryption logic

This script is educational by design and prioritizes behavioral clarity over stealth or persistence.

## High‑Level Behavior

Generates a Fernet symmetric encryption key
Encrypts files matching predefined extensions
Writes a ransom note to the filesystem
Protects the symmetric key using asymmetric cryptography
Leaves recovery intentionally dependent on key restoration

## ***The script does not***:
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

### Assumptions

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

### Design Constraints

The code is not production‑ready

No obfuscation or anti‑analysis techniques are used

The implementation prioritizes:

Readability

Traceability

## Defensive understanding

This is a learning and research artifact, not an operational tool.

Ethical and Legal Disclaimer

This project is provided strictly for educational, research, and defensive purposes.

Any use outside of authorized lab environments is unethical and potentially illegal.
I assumes no responsibility for misuse or unauthorized execution.
Repository Status
Maintained as private
Not intended for redistribution
Shared only in controlled professional or academic contexts


## QUICK DEMO.
we will select a particular folder to encrypt everything inside, From images,txt,

-Create a folder name "TEST_ENCRYPTION"  ON the Desktop

-Put or copy all types of files images,pdfs,text etc. into the folder

-change the folder path to thisself.sysRoot = os.path.join(os.path.expanduser("~"), "Desktop", "test_encryption")

-Compile and run the application but the simplest way is to run it from your idle.I will be using sublime for now

-After running check the folder to see that all files are encrypted.And also  your backgroung will change and there will be a note on the desktop.

-Now we can decrypt the files by runing the decrypter.py .NB:The decryptor.py assumes there is put_me_on_desktop.txt(which contains the private AES key).It reads the key and uses it to decrypt the fernet key and decrypts the entire files.

### A QUICK DIAGRAM IS SHOWN BELOW.
![Image ALT](https://github.com/cybernight646/offensive-security-labs/blob/d33d86ba8173221afbb21b36e6ef439809417f95/Ransomware_practical/Screenshot%20(104).png)

-SO the public key(public.pem) has to be in the same folder as the ransomware script for the encryption to be successful.

-THE encryption folder should look something like this .it should contain all types of files including executatbles .We will use this for just a demo.NB:In a target system it will encrypt on the files weve specified in the ransomware.py.
![Image ALT](https://github.com/cybernight646/offensive-security-labs/blob/598b4eb7808d9efff0ce9bfd57aadd355d1ae2e3/Ransomware_practical/Screenshot%20(105).png)

-BEFORE ENCRYPTION All the files open correctly

![Demo](https://github.com/cybernight646/offensive-security-labs/blob/94a0e6e8b9c75e90b20b0bf81799d381650a4b76/Ransomware_practical/Animation.gif)

AFTER ENCRYPTION
-RElize that there is a ransom note in the folder

![Demo ALT](https://github.com/cybernight646/offensive-security-labs/blob/8a0859191b67191a97825f08b40f141542ded3e7/Ransomware_practical/animation2.gif)


## IMPORTANT
->There easiest way to practicaly see this in action is to remove the public key from the folder that the ransomware.py will read from.
That way it will encrypt the files using the fernet key alone and the Fernet key will be unencrypted since theres no public key.

->That way just uses the decrypter.py to read the fernet key and decrypt the files easily .NB:the fernet key file should be name PUT_ME_ON_DESKTOP.txt or better still modify the code however you want.


## Defender’s View and Detection Perspective

This script is designed to simulate a real-world ransomware attack surface in a controlled and educational manner. Its purpose is to demonstrate how ransomware typically operates once it has execution within a user environment, and what defenders can realistically observe, detect, and mitigate during such an event.

Note: This implementation is intentionally non-evasive and does not attempt to bypass modern security controls. In real-world attacks, adversaries actively invest significant effort into evading detection and response mechanisms.

Encryption Approach and Initial Execution

The script uses a Fernet symmetric key to encrypt files. Symmetric encryption is commonly used by ransomware because it allows fast, large-scale encryption of files with minimal computational overhead.

At the very early stage of execution—when the key is generated—there is little immediate malicious activity. On its own, key generation does not necessarily trigger security alerts, as cryptographic operations are common in many legitimate applications.

Mass File Encryption as a Primary Detection Signal

Once encryption begins, the behavior becomes highly observable.

The script recursively walks the user’s directory and encrypts files matching a predefined list of extensions. To accelerate this process, it uses multi-threading, allowing multiple threads to encrypt files concurrently.

From a defensive standpoint, this is a strong and reliable detection signal:

A single process rapidly accessing and modifying many unrelated files

High-frequency read/write operations across multiple directories

File contents being overwritten in place at scale

Endpoint Detection and Response (EDR) solutions are specifically designed to identify this pattern. Even though only a limited number of threads are used in this example, real-world ransomware typically uses far more aggressive concurrency to maximize damage before detection. This makes mass encryption behavior one of the most effective indicators of ransomware activity.

Any process exhibiting this behavior should be immediately terminated or isolated.

Why Speed Works Against the Attacker

Ransomware relies on speed to be effective. However, that same speed works in favor of defenders.

Ransomware does not operate slowly or cautiously; it encrypts as much data as possible in the shortest time. This results in a behavior profile that is:

Noisy

Anomalous

Easily distinguishable from legitimate applications

As a result, modern EDR platforms can detect and stop ransomware mid-execution, significantly reducing the blast radius.

Importance of Application and Access Control

Most ransomware, including this simulation, operates under the current user’s security context. It does not require administrator privileges to cause significant damage.

This highlights the importance of robust access control mechanisms:

Application control to prevent unauthorized executables or scripts from running

Restricting execution from user-writable directories

Enforcing allow-listing for trusted applications only

By limiting where and how executables can run, defenders can prevent ransomware from gaining an initial foothold—even if the system is otherwise vulnerable.

Key Defensive Takeaways

From a defender’s perspective, this simulation reinforces several critical lessons:

Mass file encryption is the most reliable ransomware detection signal

Speed and concurrency increase detectability

User-context execution still poses serious risk

Application control and execution policies are essential

Early detection dramatically reduces impact

This project exists to help defenders understand these behaviors and design stronger detection, prevention, and recovery strategies.
