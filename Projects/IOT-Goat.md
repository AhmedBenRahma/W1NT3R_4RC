
# Hacking IoTGoat — OWASP IoT Top 10 Lab
 
A hands-on penetration test and firmware analysis of [OWASP IoTGoat](https://github.com/OWASP/IoTGoat), a deliberately vulnerable IoT firmware based on OpenWrt, built as a lab exercise mapped to the **OWASP IoT Top 10 (2018)**.
 
> **Status: work in progress.** This README is a scaffold — the environment is set up and the methodology below is confirmed, but the exploitation results (Hydra crack, shellback shell, `cmdinject` access, John crack) are placeholders until the lab is actually run. Every `TODO` marks a section to fill in with real command output and screenshots. Nothing below is fabricated.
 
## Overview
 
IoTGoat ships with vulnerabilities covering hardcoded credentials, a network backdoor, an unauthenticated command-injection endpoint, and weak password hashing — a compact tour of the issues real IoT devices ship with in production. This lab attacks the same virtual appliance two ways: as a black box over the network (Part 1), and as a firmware image pulled apart offline (Part 2).
 
| | |
|---|---|
| **Target** | OWASP IoTGoat (OpenWrt-based) |
| **Image** | `IoTGoat-x86.vmdk` (dynamic testing) + `IoTGoat-x86.img.gz` (static analysis) |
| **Hypervisor** | VMware Workstation (lab spec calls for VirtualBox; both work from the same `.vmdk`) |
| **Attacker tools** | Hydra, John the Ripper, binwalk, netcat |
| **Reference** | OWASP IoT Top 10 2018, OWASP Firmware Security Testing Methodology, OWASP Web Security Testing Guide |
 
## OWASP IoT Top 10 — what this lab covers
 
| ID | Risk | Hit in this lab? |
|---|---|---|
| I1 | Weak, Guessable, or Hardcoded Passwords | ✅ hardcoded web-UI password, Mirai-wordlist SSH crack attempt |
| I2 | Insecure Network Services | ✅ `shellback` backdoor service on port 5515 |
| I3 | Insecure Ecosystem Interfaces | ✅ `cmdinject` developer page reachable post-login |
| I5 | Use of Insecure or Outdated Components | ✅ MD5-crypt password hashing in `/etc/shadow` |
 
## Environment setup
 
The lab calls for VirtualBox; I built it in VMware Workstation instead using the same `.vmdk`, which meant solving the host-only networking myself rather than following the guide verbatim. Documenting that here because it's the part most writeups skip.
 
**VM configuration:**
- Type: Linux, Version: Linux 2.6/3.x/4.x (32-bit)
- 1 vCPU, 256 MB RAM (IoTGoat is a minimal OpenWrt image — this is enough)
- Disk: existing virtual disk → `IoTGoat-x86.vmdk`, kept in original format
- Network adapter: Host-only (VMnet1)
**Networking gotcha:** VMware's default Host-only subnet is *not* `192.168.1.0/24` — check `Edit → Virtual Network Editor` for the actual subnet VMnet1 is using (mine was `192.168.37.0/24`). Set a static IP on the VM to match:
 
```sh
uci set network.lan.proto='static'
uci set network.lan.ipaddr='192.168.37.10'
uci set network.lan.netmask='255.255.255.0'
uci commit network
/etc/init.d/network restart
```
 
And give the matching host-only adapter a static IP on the Windows/Linux host side so both ends sit on the same subnet. Confirm with `ip a show br-lan` in the VM and `ping` from the host.
 
`TODO`: screenshot of successful ping + the IoTGoat login page loading at the VM's IP.
 
## Part 1 — Black-box network penetration test
 
Target reached over the network only, no firmware pulled apart yet.
 
### 1.1 Hardcoded credentials + password spraying
 
`/etc/passwd` shows a non-root account, `iotgoatuser`. Rather than guess, the lab uses the leaked [Mirai botnet credential list](https://github.com/securing/mirai_credentials/blob/master/mirai_creds.txt) — the same list real Mirai-family malware uses to worm through IoT devices with default passwords — against SSH with Hydra:
 
```sh
hydra -t 4 -C mirai_creds.txt ssh://<IoTGoat-IP>
```
 
`TODO`: `/etc/passwd` content, Hydra output, cracked password (or confirmation that none of the Mirai defaults worked).
 
### 1.2 The `shellback` backdoor (I2 — Insecure Network Services)
 
```sh
netstat -antp   # run inside the VM, identifies the shellback listener on port 5515
nc -nv <IoTGoat-IP> 5515   # from the host — drops into a shell on the device
```
 
A listening service with no authentication that hands out a shell to anyone who connects is a textbook I2 finding, and it's the kind of backdoor that's shown up in real consumer routers.
 
`TODO`: `netstat` output confirming port 5515, and what the `nc` session returned.
 
### 1.3 Unauthenticated-enough command injection (I3 — Insecure Ecosystem Interfaces)
 
After logging into the LuCI web UI (`root` / `iotgoathardcodedpassword.`), a developer debug page is reachable at a path that isn't linked from the UI and isn't access-controlled beyond the initial login:
 
```
https://<IoTGoat-IP>/cgi-bin/luci/admin/iotgoat/cmdinject
```
 <img width="770" height="262" alt="image" src="https://github.com/user-attachments/assets/b0b5384c-9cd6-4907-8e78-c0c422ba4e67" />

The path itself was found by analyzing the firmware (Part 2), not guessed — a good illustration of why I3 says "insecure interfaces," not just "missing login screen": the page assumes obscurity is protection.
 
`TODO`: screenshot of the page, and what commands could be executed through it.
 
## Part 2 — Static firmware analysis
 
Same device, attacked from the firmware image instead of the network.
 
### 2.1 Extracting the firmware
 
```sh
gunzip IoTGoat-x86.img.gz | binwalk -ev
```
 
`binwalk` identifies and carves out embedded filesystems from the firmware blob — here, a SquashFS root filesystem (`squashfs-root/`).
 
`TODO`: binwalk output, confirming the squashfs offset/extraction.
 
### 2.2 Reading the shadow file (I1 + I5)
 
`squashfs-root/etc/shadow` holds MD5-crypt (`$1$`) hashes for `root` and `iotgoatuser`:
 
```
root:$1$Jl7H1VOG$Wgw2F/C.nLNTC.4pwDa4H1:...
iotgoatuser:$1$79bz0K8z$Ii6Q/if83F1QodGmkb4Ah.:...
```
 
MD5-crypt is a weak, fast-to-brute-force hashing scheme by modern standards (I5 — Insecure/Outdated Components) — bcrypt/scrypt/argon2 exist precisely to make offline cracking expensive, and this firmware ships with none of them.
 
### 2.3 Cracking with John + the Mirai wordlist
 <img width="811" height="162" alt="image" src="https://github.com/user-attachments/assets/ddeb6be5-3aae-4429-a6dd-13dc56d17054" />

```sh
john --wordlist=mirai_creds.txt squashfs-root/etc/shadow
```
 
`TODO`: John output — cracked password(s), or "no password hashes cracked" if the Mirai list didn't contain a match for this particular build.
 
## Findings summary
 
| Finding | OWASP IoT Top 10 | Severity | Fix |
|---|---|---|---|
| Hardcoded web-UI password | I1 | High | Force unique per-device credentials at first boot |
| `shellback` unauthenticated shell on 5515 | I2 | Critical | Remove debug backdoors before shipping; firewall internal services |
| `cmdinject` reachable post-login, unlinked | I3 | High | Proper authorization checks per-endpoint, not just "not in the menu" |
| MD5-crypt password hashing | I5 | Medium | Use bcrypt/scrypt/argon2 for credential storage |
| `TODO` — SSH password crack result | I1 | — | Depends on result |
 
## What I learned
 
`TODO` — a few sentences once Parts 1–2 are actually run: what surprised you, what took longest (the networking setup, probably), what you'd check first on a real device after this.
 
## References
 
- [OWASP IoTGoat](https://github.com/OWASP/IoTGoat)
- [OWASP IoT Top 10 (2018)](https://owasp.org/www-pdf-archive/OWASP-IoT-Top-10-2018-final.pdf)
- [OWASP Firmware Security Testing Methodology](https://github.com/scriptingxss/owasp-fstm)
- [OWASP Web Security Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)
- [Mirai credential list](https://github.com/securing/mirai_credentials)
 
