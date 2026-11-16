
# Lab 3 : ECC et cryptographie à base de couplages (Pairing-Based Cryptography)
 
> Cours **IoT Security** · ENSI (École Nationale des Sciences de l'Informatique) · 2026
> Auteur : **Ahmed Ben Rahma**
 
Ce dépôt documente, étape par étape, la réalisation du Lab 3 : installation de la bibliothèque **PBC** (Pairing-Based Cryptography), vérification de la propriété fondamentale des couplages bilinéaires, test d'un schéma de signature existant (BLS) et implémentation du cryptosystème **Boneh-Franklin IBE (BF-IBE)** en C.
 
---
 
## Sommaire
 
1. [Objectifs](#1-objectifs)
2. [Notions clés (en termes simples)](#2-notions-clés-en-termes-simples)
3. [Environnement](#3-environnement)
4. [Installation](#4-installation)
5. [Partie 1 : vérifier la propriété du couplage](#5-partie-1--vérifier-la-propriété-du-couplage)
6. [Partie 2 : tester un exemple (signature BLS)](#6-partie-2--tester-un-exemple-signature-bls)
7. [Partie 3 : implémentation de BF-IBE](#7-partie-3--implémentation-de-bf-ibe)
8. [Problèmes rencontrés et solutions](#8-problèmes-rencontrés-et-solutions)
9. [Structure du dépôt](#9-structure-du-dépôt)
10. [Conclusion](#10-conclusion)
11. [Références](#11-références)
---
 
## 1. Objectifs
 
| Partie | Objectif |
|---|---|
| Installation | Mettre en place GMP et PBC sur Linux |
| Partie 1 | Vérifier la bilinéarité : `e(g^a, h^b) = e(g, h)^(a·b)` |
| Partie 2 | Identifier et tester un algorithme cryptographique des exemples PBC |
| Partie 3 | Implémenter le cryptosystème BF-IBE (Setup, Extract, Encrypt, Decrypt) |
 
---
 
## 2. Notions clés (en termes simples)
 
**Courbe elliptique (ECC).** Un ensemble de points sur lequel on peut faire des calculs. Il est très difficile de retrouver `x` à partir de `x·P`, et c'est cette difficulté qui protège les clés.
 
**Couplage bilinéaire (pairing).** Une fonction `e(·,·)` qui prend deux points de courbes (`G1` et `G2`) et renvoie un élément d'un autre groupe (`GT`). Sa propriété magique est la **bilinéarité** :
 
```
e(g^a, h^b) = e(g, h)^(a·b)
```
 
On peut donc « sortir » les exposants `a` et `b` du couplage. Presque toute la cryptographie à base de couplages repose sur cette égalité.
 
**IBE (Identity-Based Encryption).** Un chiffrement où la clé publique est simplement l'identité de la personne (par exemple son e-mail). Il n'y a pas besoin de certificat : une autorité de confiance (le PKG) génère la clé privée correspondante.
 
---
 
## 3. Environnement
 
- Système : Linux (Kali sous WSL)
- Bibliothèques : **GMP** (grands nombres) et **PBC 0.5.14**
- Outils : `gcc`, `make`, `m4`, `flex`, `bison`
---
 
## 4. Installation
 
### 4.1 Dépendances
 
```bash
sudo apt-get install m4 flex bison build-essential
sudo apt install libgmp-dev
```
 
> GMP est installé via `apt` (`libgmp-dev`). La compilation manuelle de GMP 6.3.0 a échoué avec le GCC récent (voir [section 8](#8-problèmes-rencontrés-et-solutions)).
 
![Installation des dépendances]<img width="1012" height="367" alt="image" src="https://github.com/user-attachments/assets/d284a087-e2c0-45f1-9a82-c22f1551beee" />

 
### 4.2 Installation de PBC
 
```bash
cd ~
wget https://crypto.stanford.edu/pbc/files/pbc-0.5.14.tar.gz
tar -xzf pbc-0.5.14.tar.gz
cd pbc-0.5.14
./configure && make && sudo make install
```
<img width="997" height="230" alt="image" src="https://github.com/user-attachments/assets/ecfca122-96bc-4440-b751-cf1f1d1abfd6" />


 
### 4.3 Configuration de la bibliothèque dynamique
 
```bash
echo "/usr/local/lib" | sudo tee /etc/ld.so.conf.d/newlib.conf
sudo ldconfig
```
 
Cette étape indique au système où trouver `libpbc` après l'installation.
<img width="820" height="138" alt="image" src="https://github.com/user-attachments/assets/b526b009-2fb1-4685-aef8-f08336177aeb" />

 
### 4.4 Vérification
 
```bash
./pbc/pbc
```
 
Le programme se lance et attend des commandes : PBC est opérationnel.
 
![PBC en marche](<img width="486" height="55" alt="image" src="https://github.com/user-attachments/assets/a8af2633-9149-4d9b-93bc-39cd07a3e291" />

 
---
 
## 5. Partie 1 : vérifier la propriété du couplage
 
### 5.1 Test automatique fourni
 
```bash
cd ~/pbc-0.5.14
./pbc/pbc pbc/pairing_test.pbc < param/a.param
```
 
Chaque ligne affichant `1` correspond à un test de bilinéarité réussi (1 = vrai).
 
![Résultat de pairing_test.pbc](<img width="622" height="275" alt="image" src="https://github.com/user-attachments/assets/6fe3fc8a-effe-4435-a3ba-95cabbaeef8e" />

 
### 5.2 Vérification manuelle
 
Lancer `./pbc/pbc`, puis saisir :
 
```
g:=rnd(G1);
h:=rnd(G2);
a:=rnd(Zr);
b:=rnd(Zr);
g;
h;
a;
b;
pairing(g,h);
pairing(g^a,h^b);
pairing(g,h)^(a*b);
```
 
> Les affectations (`g:=...`) n'affichent rien. Pour voir une valeur, on la saisit seule (`g;`).
 
**Explication.**
- `rnd(G1)` et `rnd(G2)` tirent des points aléatoires ; `rnd(Zr)` tire un entier aléatoire.
- `pairing(g^a, h^b)` applique le couplage aux points élevés aux puissances `a` et `b`.
- `pairing(g,h)^(a*b)` élève le couplage de départ à la puissance `a·b`.
**Résultat attendu :** les deux dernières lignes sont **strictement identiques**, ce qui prouve la bilinéarité. Les valeurs changent à chaque exécution car `rnd` est aléatoire.
 
![Vérification de la bilinéarité](<img width="1462" height="425" alt="image" src="https://github.com/user-attachments/assets/bacc9dfe-da06-4298-abdc-00a89e094876" />

 
---
 
## 6. Partie 2 : tester un exemple (signature BLS)
 
Le dossier `example/` contient plusieurs implémentations (BLS, ZSS, Hess, Paterson, Zhang-Kim, Yuan-Li, Joux). Un seul algorithme est testé ici : **BLS**.
 
```bash
cd ~/pbc-0.5.14
./example/bls < param/d159.param
```
 
![Exécution de l'exemple BLS](images/06-bls.png)
 
### Algorithme : signature courte BLS (Boneh-Lynn-Shacham)
 
| Étape | Description |
|---|---|
| Clé privée | un entier secret `x` |
| Clé publique | `pk = g^x` |
| Signature | `σ = H(m)^x`, où `H(m)` est le hash du message converti en point de la courbe |
| Vérification | `e(σ, g) = e(H(m), pk)` |
 
**Pourquoi la vérification fonctionne.** Par bilinéarité : `e(H(m)^x, g) = e(H(m), g)^x = e(H(m), g^x) = e(H(m), pk)`.
 
### Lecture de la sortie
 
- `f(sig, g)` et `f(message hash, public_key)` sont **égaux**, d'où `signature verifies`.
- `random signature doesn't verify` : une fausse signature est rejetée.
- La signature est aussi **compressée** puis décompressée (`compressed` / `decompressed`) : elle tient sur environ 21 octets.
---<img width="1481" height="627" alt="image" src="https://github.com/user-attachments/assets/96122a72-7d43-4a16-a55c-15ddb1cf2cb5" />

 
## 7. Partie 3 : implémentation de BF-IBE
 
Implémentation du schéma **BasicIdent** de Boneh-Franklin.
 
### 7.1 Principe
 
| Étape | Qui | Calcul |
|---|---|---|
| **Setup** | Autorité (PKG) | Choisit `P` et une clé maître secrète `s`. Publie `Ppub = s·P` |
| **Extract** | PKG | Pour une identité `ID` : `Qid = H1(ID)`, clé privée `did = s·Qid` |
| **Encrypt** | Expéditeur | Choisit `r`. `U = r·P`, `V = M ⊕ H2( e(Qid, Ppub)^r )` |
| **Decrypt** | Destinataire | `M = V ⊕ H2( e(did, U) )` |
 
**Pourquoi le déchiffrement fonctionne.** Par bilinéarité :
 
```
e(did, U) = e(s·Qid, r·P) = e(Qid, P)^(s·r) = e(Qid, s·P)^r = e(Qid, Ppub)^r
```
 
Les deux côtés calculent la même valeur, donc le masque `H2(...)` est identique et le XOR retrouve `M`.
 
### 7.2 Code source (`bfibe.c`)
 
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <pbc/pbc.h>
 
int main(void) {
  pairing_t pairing;
  char param[1024];
  size_t count = fread(param, 1, 1024, stdin);
  if (!count) pbc_die("input error");
  pairing_init_set_buf(pairing, param, count);
 
  element_t P, s, Ppub, Qid, did, r, U, g1, g2;
  element_init_G1(P, pairing);   element_init_G1(Ppub, pairing);
  element_init_G1(Qid, pairing); element_init_G1(did, pairing);
  element_init_G1(U, pairing);
  element_init_Zr(s, pairing);   element_init_Zr(r, pairing);
  element_init_GT(g1, pairing);  element_init_GT(g2, pairing);
 
  /* Setup : P aleatoire, cle maitre s, cle publique Ppub = s.P */
  element_random(P);
  element_random(s);
  element_pow_zn(Ppub, P, s);
 
  /* Extract : Qid = H1(ID), did = s.Qid */
  const char *id = "ahmed@ensi.tn";
  element_from_hash(Qid, (void *)id, strlen(id));
  element_pow_zn(did, Qid, s);
 
  /* Encrypt : U = r.P, V = M xor H2(e(Qid,Ppub)^r) */
  const char *msg = "Hello IBE";
  int mlen = strlen(msg);
  unsigned char V[64], M2[64];
  element_random(r);
  element_pow_zn(U, P, r);
  pairing_apply(g1, Qid, Ppub, pairing);
  element_pow_zn(g1, g1, r);
  int len = element_length_in_bytes(g1);
  unsigned char *buf = malloc(len);
  element_to_bytes(buf, g1);
  for (int i = 0; i < mlen; i++) V[i] = msg[i] ^ buf[i];
 
  /* Decrypt : M = V xor H2(e(did,U)) */
  pairing_apply(g2, did, U, pairing);
  element_to_bytes(buf, g2);
  for (int i = 0; i < mlen; i++) M2[i] = V[i] ^ buf[i];
  M2[mlen] = 0;
 
  printf("ID       : %s\n", id);
  printf("Message  : %s\n", msg);
  printf("Dechiffre: %s\n", M2);
  printf(element_cmp(g1, g2) == 0 ? "OK : e(Qid,Ppub)^r == e(did,U)\n" : "ECHEC\n");
  return 0;
}
```
 
 
### 7.3 Compilation et exécution
 
```bash
gcc bfibe.c -o bfibe -I/usr/local/include -L/usr/local/lib -lpbc -lgmp
./bfibe < param/a.param
```
 
**Sortie obtenue :**
 
```
ID       : ahmed@ensi.tn
Message  : Hello IBE
Dechiffre: Hello IBE
OK : e(Qid,Ppub)^r == e(did,U)
```
 
![Exécution de BF-IBE](<img width="915" height="166" alt="image" src="https://github.com/user-attachments/assets/7ce418dd-ac85-4833-a6b1-21e1ba74fb6c" />

 
### 7.4 Limites de cette implémentation
 
- `H1` est réalisée avec `element_from_hash` (identité vers un point de `G1`).
- `H2` est **simplifiée** : les octets de l'élément de `GT` servent directement de masque, sans passer par une fonction de hachage (comme SHA-256).
- Le message est limité à la longueur de l'élément de `GT`.
- Il s'agit de la version **BasicIdent**, sécurisée contre les attaques à clair choisi seulement. La version **FullIdent** ajoute la sécurité contre les attaques à chiffré choisi.
Ces simplifications sont acceptables dans le cadre pédagogique du lab, mais ne conviennent pas à un usage en production.
 
---
 
## 8. Problèmes rencontrés et solutions
 
| Problème | Cause | Solution |
|---|---|---|
| `./configure: No such file or directory` | Commande lancée hors du dossier extrait | Se placer dans le dossier (`cd gmp-6.3.0`) |
| GMP : `could not find a working compiler` | Incompatibilité du test `configure` de GMP 6.3.0 avec le GCC récent | Installer GMP par `apt` : `sudo apt install libgmp-dev` |
| PBC (dépôt Git) : `Missing AX_CXX_COMPILE_STDCXX_14` | Paquet autotools manquant | Utiliser l'archive officielle `pbc-0.5.14.tar.gz` qui contient déjà `configure` |
| `syntax error, unexpected ID` | Un fichier `.param` passé en argument de `pbc` est lu comme un script de commandes | Les paramètres se passent en entrée standard : `./pbc/pbc script.pbc < param/a.param` |
 
---
 
## 9. Structure du dépôt
 
```
.
├── README.md
├── bfibe.c            # Implémentation BF-IBE (BasicIdent)
└── images/            # Captures d'écran de chaque étape
    ├── 01-install-dependances.png
    ├── 02-install-pbc.png
    ├── 03-pbc-lance.png
    ├── 04-pairing-test.png
    ├── 05-bilinearite.png
    ├── 06-bls.png
    ├── 07-code-bfibe.png
    └── 08-execution-bfibe.png
```
 
---
 
## 10. Conclusion
 
Ce lab a permis de :
 
- installer et utiliser la bibliothèque **PBC** pour manipuler des couplages bilinéaires ;
- **vérifier expérimentalement** la propriété `e(g^a, h^b) = e(g, h)^(a·b)` ;
- comprendre le fonctionnement d'une **signature courte BLS** ;
- implémenter de bout en bout un schéma de **chiffrement basé sur l'identité (BF-IBE)** : la clé publique d'un utilisateur est son identité, et le déchiffrement repose entièrement sur la bilinéarité du couplage.
---
 
## 11. Références
 
- Boneh, D., Franklin, M. *Identity-Based Encryption from the Weil Pairing*, CRYPTO 2001.
- Boneh, D., Lynn, B., Shacham, H. *Short Signatures from the Weil Pairing*, ASIACRYPT 2001.
- PBC Library : <https://crypto.stanford.edu/pbc/>
- GMP : <https://gmplib.org/>
 
