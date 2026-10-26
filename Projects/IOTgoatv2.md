
# IoTGoat Pentest — OWASP IoTGoat Lab Writeup
 
Writeup du TP "Hacking IoTGoat" — exploitation de firmware/VM volontairement vulnérable (OWASP IoT Top 10 2018), environnement VMware (NAT) sous Windows + Kali/WSL.
 
**Cible :** [OWASP IoTGoat](https://github.com/OWASP/IoTGoat) — firmware OpenWrt vulnérable à des fins pédagogiques.
 
**Catégories OWASP IoT Top 10 couvertes :** I1 (Weak, Guessable, or Hardcoded Passwords), I3 (Insecure Ecosystem Interfaces), I9 (Insecure Default Settings).
 
---
 
## Environnement
 
- Hyperviseur : VMware Workstation
- Image cible : `IoTGoat-x86.vmdk` / `IoTGoat-x86.img.gz`
- Machine d'attaque : Kali / WSL (Ubuntu)
- Réseau : NAT (VMnet8), VM obtenue en IP `192.168.147.129`
> Note technique : la connectivité host↔VM a initialement échoué en mode Bridged sur WiFi (aucune réponse DHCP). Résolu en passant en mode NAT et en vérifiant que les services Windows `VMware NAT Service` et `VMware DHCP Service` étaient bien démarrés.
 
![Boot de la VM IoTGoat]
<img width="852" height="387" alt="image" src="https://github.com/user-attachments/assets/78dda3a0-a269-4556-af29-a62835cee5cf" />

*Démarrage de la VM, banner OWASP IoTGoat et shell BusyBox.*
 
---
 
## Partie 1 — Pentest dynamique sur la VM
 
### 1. Découverte du compte applicatif
 
```
cat /etc/passwd
```
 
Un utilisateur `iotgoatuser` est présent — candidat pour une attaque par dictionnaire.
 
![cat /etc/passwd dans la VM]
<img width="586" height="196" alt="image" src="https://github.com/user-attachments/assets/7b524c16-20c2-4d36-b557-ee597b73273c" />

 
### 2. Brute-force SSH avec Hydra
 
Wordlist utilisée : [`mirai_creds.txt`](https://github.com/securing/mirai_credentials/blob/master/mirai_creds.txt) (identifiants par défaut du botnet Mirai).
 
```
hydra -t 4 -C mirai_creds.txt ssh://192.168.147.129
```
 
![Résultat Hydra - credentials SSH trouvés]
<img width="1467" height="275" alt="image" src="https://github.com/user-attachments/assets/56e6dd53-3233-4994-b368-9201c319d387" />

*Hydra trouve un couple login/mot de passe valide pour `iotgoatuser`.*
 
**Constat :** mot de passe faible et présent dans une wordlist publique de credentials par défaut → I1.
 
### 3. Backdoor réseau non authentifiée (shellback)
 
Identification du service sur la VM :
 
```
netstat -antp
```
 
![netstat -antp - port 5515 shellback]
<img width="923" height="453" alt="image" src="https://github.com/user-attachments/assets/975bff07-5150-492a-a898-029502d6ed79" />

*Port `5515` ouvert, process `shellback`.*
 
Connexion depuis le host :
 
```
nc -nv 192.168.147.129 5515
```
 
![Connexion au backdoor shellback]

<img width="682" height="102" alt="image" src="https://github.com/user-attachments/assets/cd469d2f-70af-4e5d-9850-9698f777424a" />

*Accès shell direct sans authentification.*
 
**Constat :** backdoor réseau non documentée, sans authentification → I2 / I9.
 
### 4. Exécution de commandes via l'interface web (cmdinject)
 
Authentification sur l'interface web (`https://192.168.147.129`) avec les identifiants hardcodés connus du firmware :
 
- Utilisateur : `root`
- Mot de passe : `iotgoathardcodedpassword.`
![Login web IoTGoat]
<img width="1702" height="771" alt="image" src="https://github.com/user-attachments/assets/8ee7a968-4ae0-473d-8bb6-b0d2d7de412a" />

 
Accès à la page de debug non protégée :
 
```
https://192.168.147.129/cgi-bin/luci/admin/iotgoat/cmdinject
```
 
![Page cmdinject accessible](
*Page de développement laissée accessible en production, permettant l'injection de commandes.*
 
**Constat :** contrôle d'accès insuffisant sur une interface de debug exposée → I3.
 
---
 
## Partie 2 — Analyse statique du firmware
 
### 1. Extraction du firmware
 
```
gunzip IoTGoat-x86.img.gz
binwalk -e IoTGoat-x86.img
```
 
![Extraction binwalk]

<img width="1477" height="182" alt="image" src="https://github.com/user-attachments/assets/80dfd83e-1f29-484b-93e6-af2d9707dd18" />

*Détection d'un filesystem EXT et extraction du système de fichiers SquashFS (`squashfs-root`).*
 
### 2. Récupération des hashes de mots de passe
 
```
cat squashfs-root/etc/shadow
cat squashfs-root/etc/passwd
```
 
![Contenu de /etc/shadow extrait du firmware]
 
Hashes au format `$1$<salt>$<hash>` → algorithme MD5-crypt, pour les comptes `root` et `iotgoatuser`.
 
### 3. Cassage avec John the Ripper
 
```
unshadow squashfs-root/etc/passwd squashfs-root/etc/shadow > hashes.txt
cut -d: -f2 mirai_creds.txt | sort -u > mirai_passwords.txt
john --wordlist=mirai_passwords.txt hashes.txt
john --show hashes.txt
```
 
![John the Ripper - mots de passe cassés]
<img width="1362" height="292" alt="image" src="https://github.com/user-attachments/assets/8284ddbc-3326-43f5-a0c0-38c928c67b11" />

*Les mots de passe `root` et/ou `iotgoatuser` cassés à partir du dictionnaire Mirai, confirmant le résultat obtenu dynamiquement via Hydra.*
 
---
 
## Synthèse
 
| Vulnérabilité | Méthode | Catégorie OWASP IoT Top 10 |
|---|---|---|
| Mot de passe SSH faible | Hydra + mirai_creds.txt | I1 |
| Backdoor non authentifiée (port 5515) | netstat + netcat | I2 / I9 |
| Page de debug exposée (cmdinject) | Analyse interface web | I3 |
| Mot de passe hardcodé dans le firmware | binwalk + John | I1 / I9 |
 
Ce TP illustre concrètement pourquoi les mots de passe par défaut/hardcodés et les interfaces de debug laissées actives en production restent parmi les vecteurs d'attaque les plus exploités sur les objets connectés (cf. botnet Mirai).
 
---
 
## Références
 
- [OWASP IoTGoat](https://github.com/OWASP/IoTGoat)
- [OWASP Firmware Security Testing Methodology](https://github.com/OWASP/owasp-fstm)
- [OWASP Web Security Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)
- [Mirai default credentials list](https://github.com/securing/mirai_credentials)
 
