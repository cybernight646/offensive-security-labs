Requirements
Intended Use Environment

This project is designed exclusively for red team research and defensive analysis.

Execution must occur only within a controlled lab environment on systems that are owned by, or explicitly authorized for testing by, the researcher.

The code is not designed for production systems and must not be executed on personal or third‑party machines.

Operating System

Microsoft Windows (required)

The code relies on Windows‑specific APIs and behaviors and is not portable to other platforms.

Execution Scope

File operations are scoped to a user‑defined test directory.

The script assumes the researcher will restrict execution to non‑sensitive sample data created for testing purposes.

System‑wide execution is explicitly out of scope for responsible use.

Cryptographic Assumptions

The project relies on a hybrid cryptographic design:

Symmetric encryption for file operations

Asymmetric cryptography for key protection

An RSA public key is expected to be present in the execution directory at runtime.

Private key handling, recovery workflows, and key escrow mechanisms are intentionally excluded from this repository.

Proper key generation, storage, and lifecycle management are assumed to follow standard cryptographic best practices in a research environment.

Python Runtime

Python 3.x is required.

Python Dependencies

The following third‑party libraries are required for the codebase to function as designed:

cryptography

pycryptodome

pywin32

requests

concurrent.futures (standard library)

Environment setup and dependency management are assumed to be handled by the researcher.

Design Constraints

The code is intentionally not hardened, obfuscated, or production‑ready.

The implementation prioritizes behavioral clarity to support analysis, detection engineering, and defensive learning.

This repository is maintained as private by design and is not intended for redistribution.
