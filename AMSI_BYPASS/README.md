AMSI Memory Patching – Research Artifact
Overview

This project is a research artifact created to study how the Windows Antimalware Scan Interface (AMSI) operates internally and how in-memory tampering techniques can interfere with runtime security controls.

The primary goal is defensive understanding: to analyze attacker tradecraft so that detection, monitoring, and mitigation strategies can be improved.

This code is not intended for public distribution, real-world deployment, or use outside of controlled laboratory environments on systems that the researcher explicitly owns or is authorized to test.

Purpose

To understand how AMSI integrates with user-mode processes such as PowerShell

To analyze how attackers attempt to bypass runtime scanning via process memory manipulation

To study behavioral indicators that modern EDR and endpoint protection solutions can detect

To support defensive research, detection engineering, and incident response training

High-Level Behavior (Conceptual)

At a conceptual level, this program:

Identifies a running PowerShell process

Enumerates loaded modules to locate the AMSI library

Searches process memory for a known function pattern

Modifies memory at runtime to alter AMSI behavior within that single process

The modification is process-local, memory-only, and non-persistent.

Scope and Limitations

Effects are limited to a single running process

No persistence across reboots or process restarts

No kernel-mode interaction

No disk-level modification of AMSI or Defender components

Highly sensitive to OS version, AMSI updates, and endpoint security controls

This technique is fragile by design and primarily useful for educational analysis.

Defensive Relevance

From a defensive standpoint, this project highlights:

Indicators of malicious process memory access

Detection opportunities around OpenProcess, VirtualProtectEx, and WriteProcessMemory

AMSI tampering heuristics used by modern EDR platforms

Why in-memory bypasses are increasingly unreliable against current defenses

Intended Audience

Blue team engineers

Detection and response analysts

Red team researchers in authorized environments

Security recruiters evaluating low-level Windows internals knowledge

Usage Restrictions

Private research only

Authorized systems only

Controlled lab environments

No redistribution

No operational use

Any use outside these constraints is explicitly discouraged.
