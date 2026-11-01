# Y4G4M1: ISC2 CC revision, Day 1 (2026-11-01)
 
Exam: **ISC2 Certified in Cybersecurity (CC)**, Wednesday 2026-11-04, 08:00, Université Centrale.
Goal today: go from zero revision to a solid base on Domains 1 to 3, using short summaries and practice questions.
 
## Exam facts
- Multiple choice, around 100 to 125 questions, 2 hours, passing score 700/1000.
- New exam outline effective 2026-09-01. Five domains, with AI concepts woven through all of them and cloud added to the network domain.
- Incident response content now sits inside Security Operations.
- Known weights: Security Principles 24%, Security Governance 17.3%, IAM concepts 20%.
## Domain 1: Security Principles
 
### Risk management (easy version)
- **Asset**: what we protect. **Threat**: what can cause harm. **Vulnerability**: a weakness. **Likelihood** and **impact** measure how probable and how bad.
- Risk needs both a threat and a vulnerability.
- Steps: identify, assess, prioritize, treat, monitor.
- **Qualitative** = low/medium/high scales. **Quantitative** = money: SLE = asset value x exposure factor, ALE = SLE x ARO.
- Four treatments:
  - Avoid: stop the activity.
  - Mitigate: add controls.
  - Transfer: insurance or outsourcing.
  - Accept: live with it.
- **Inherent risk** (before controls) vs **residual risk** (after controls, never zero).
- **Risk appetite** = how much risk the organization will take. **Risk register** = list of risks with owner and treatment.
- A control should not cost more than the loss it prevents.
## Domain 2: Incident Response, Business Continuity and Disaster Recovery
 
### Incident terminology
| Term | Meaning |
|---|---|
| Event | Any observable occurrence in a system or network |
| Incident | An event that actually or potentially harms confidentiality, integrity or availability |
| Breach | Unauthorized access or disclosure, mainly of personal data |
| Intrusion | Deliberate attempt to access a system without permission |
| Threat | Anything with potential to cause harm |
| Vulnerability | A weakness that could be exploited |
| Exploit | The specific attack that uses a vulnerability |
| Zero day | A previously unknown vulnerability with no patch or signature |
 
Chain: every incident is an event, but not every event is an incident. A breach is a serious type of incident.
 
### BC vs DR
- **Business Continuity (BCP)**: keep critical business functions running. Mostly a business function, built with people from across the organization.
- **Disaster Recovery (DRP)**: restore IT and communications to full, last-known reliable operations. It steps in where BC leaves off.
### BCP components
- BCP team list with multiple contact methods and backup members.
- Guidance for management and delegated authority.
- Supply chain contacts: vendors, customers, emergency providers, partners.
- How and when to enact the plan.
- Immediate response procedures and checklists (safety, fire suppression, notifying emergency agencies).
- Notification systems and call trees.
### Other points from the course questions
- **Red book**: a hard copy of the BCP kept outside the facility as a backup.
- **BIA (Business Impact Analysis)**: identifies critical functions and their dependencies.
- BCP efforts need support from **executive management or an executive sponsor**.
- **DRP executive summary**: a short high-level overview for senior management.
- **Incident response phases**: Preparation, Detection and Analysis, Containment/Eradication/Recovery, Post-incident Activity.
## Domain 3: Access Control Concepts
- **Subject**: the active entity that requests access (user, program).
- **Object**: the passive entity being accessed and that responds to the request (file, database, printer).
- **Least privilege**: users get only the access they need for their job. It can be limited by time, by fields, or by relationship (a doctor sees only their own patients). Access attempts are logged, and critical data needs stronger protection such as MFA.
- **MAC (Mandatory Access Control)**: a central authority sets permissions from classifications or security labels, enforced system-wide. Users and data owners cannot change them (for example security clearances). Often paired with separation of duties and RBAC.
## Practice
- Took quizzes on risk management and incident terminology.
- Answered course questions on red book, BIA, executive support, incident response phases, subjects and objects.
## Still to do before Wednesday
- Domain 3: DAC, RBAC, physical access controls, MFA, account management.
- Domain 4: network security (OSI, ports, firewalls, IDS/IPS, cloud models).
- Domain 5: security operations (encryption, hashing, logging, patching, awareness).
- Rest of Domain 2: recovery strategies.
- Take the portal's final assessment and review mistakes.
- Sleep early on Tuesday.
