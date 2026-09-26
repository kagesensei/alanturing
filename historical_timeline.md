# Historical Timeline of Cybersecurity: From Turing Machines to Bio-Hybrid Frontiers

This timeline follows the development of cybersecurity from early computation and wartime cryptanalysis to current security challenges. Alan Turing is a central starting point because his work helped establish theoretical computation and contributed to Allied cryptanalysis during the Second World War. Modern cybersecurity was shaped by many people and fields over several decades, so the connections to Turing below are identified as direct influence, conceptual parallels or later developments.

The timeline includes links for students and anyone who wants to explore the history in more depth. Emerging research and proposed risks are identified so readers can distinguish them from demonstrated results.

---

## 1. Foundations and Mechanical Cryptanalysis (1930s to 1950s)

### 1936 | [Alan Turing](https://en.wikipedia.org/wiki/Alan_Turing)
* **Milestone:** 
  * Formulation of the Universal Turing Machine and the Halting Problem
  * Published in [On Computable Numbers, with an Application to the Entscheidungsproblem](https://londmathsoc.onlinelibrary.wiley.com/doi/10.1112/plms/s2-42.1.230)
* **Paradigm Shift:** Proved that a single theoretical machine could execute any computable sequence
  * [Turing Machine Architecture](https://en.wikipedia.org/wiki/Turing_machine)
  * Established formal state transitions, stored programs and theoretical limits on decidability
  * These ideas provide a conceptual foundation for later analysis of programs and machine behavior
* **Lineage:** Established the formal mathematics of computation
  * [The Halting Problem](https://en.wikipedia.org/wiki/Halting_problem)
  * Later results such as [Rice's Theorem](https://en.wikipedia.org/wiki/Rice%27s_theorem) show that no general algorithm can decide every nontrivial semantic property of every program
  * This is a theoretical limit under specific assumptions, not a claim that static analysis cannot detect malicious code
  * Static analysis remains useful for finding known patterns, policy violations and some classes of vulnerabilities

### 1932 to 1945 | [Marian Rejewski](https://en.wikipedia.org/wiki/Marian_Rejewski), Alan Turing, [Gordon Welchman](https://en.wikipedia.org/wiki/Gordon_Welchman) and the Bletchley Park teams
* **Milestone:** Polish cryptologists including Rejewski developed methods and machinery that helped break Enigma before the war. In 1939 they shared their work with British and French allies. At Bletchley Park, Turing, Welchman and many colleagues advanced the cryptanalysis and its operational use
  * [The Cryptanalytic Bombe](https://en.wikipedia.org/wiki/Bombe)
  * [Banburismus Statistical Testing](https://en.wikipedia.org/wiki/Banburismus)
* **Paradigm Shift:** The work helped move cryptanalysis from manual analysis toward mechanized searches and statistical scoring
  * Banburismus used a statistical scoring method expressed in bans and decibans
  * The Bombe used known plaintext and logical contradictions to narrow possible settings
  * Enigma's no-self-encipherment property was one exploitable weakness, not a complete explanation for the breaks
* **Connection to Turing:** The Bletchley Park effort became a large scale intelligence operation. Turing made major contributions to a wider Allied team whose work built on earlier Polish cryptanalysis

### 1948 to 1949 | [Claude Shannon](https://en.wikipedia.org/wiki/Claude_Shannon)
* **Milestone:** Foundational papers establishing Information Theory
  * [A Mathematical Theory of Communication (1948)](https://ieeexplore.ieee.org/document/6773024)
  * [Communication Theory of Secrecy Systems (1949)](https://ieeexplore.ieee.org/document/6773027)
* **Paradigm Shift:** Founded mathematical Information Theory
  * Shannon formalized entropy, redundancy and information theoretic security in the [One Time Pad](https://en.wikipedia.org/wiki/One-time_pad)
  * Formally defined the principles of [Confusion and Diffusion](https://en.wikipedia.org/wiki/Confusion_and_diffusion)
* **Lineage:** Bridges Turing's statistical cryptanalysis into rigorous mathematical bounds on cipher entropy and computational work factors

---

## 2. Digital and Mainframe Revolution (1960s to 1980s)

### 1973 | David Bell and Leonard LaPadula
* **Milestone:** 
  * Formal security modeling for multi user computer systems
  * [The Bell LaPadula Security Model Technical Report (DTIC)](https://apps.dtic.mil/sti/citations/AD0770768)
* **Paradigm Shift:** Established the first mathematical formalization of Multi Level Security and Mandatory Access Control for multi user operating systems under DoD contracts
* **Core Rule:** Mathematical confidentiality enforcement across system states
  * Simple Security Property prohibiting unauthorized reading up
  * Star Property prohibiting unauthorized writing down

### 1976 | [Whitfield Diffie](https://en.wikipedia.org/wiki/Whitfield_Diffie), [Martin Hellman](https://en.wikipedia.org/wiki/Martin_Hellman) and [Ralph Merkle](https://en.wikipedia.org/wiki/Ralph_Merkle)
* **Milestone:** 
  * The foundation of asymmetric cryptography
  * [New Directions in Cryptography (IEEE)](https://ieeexplore.ieee.org/document/1055638)
* **Paradigm Shift:** Solved the key distribution problem over untrusted communication channels
  * Diffie-Hellman is a key agreement protocol based on the discrete logarithm problem, not a trapdoor function
  * Key agreement alone does not authenticate the parties and is vulnerable to a man in the middle attack without authentication
  * [Diffie-Hellman Key Exchange](https://en.wikipedia.org/wiki/Diffie%E2%80%93Hellman_key_exchange) is based on a one way problem but does not use a trapdoor function
  * Merkle developed cryptographic puzzles and [Merkle Trees](https://en.wikipedia.org/wiki/Merkle_tree), which support efficient integrity checks
* **Lineage:** Shifted cryptography from symmetric shared secrets to asymmetric mathematical hardness assumptions

### 1977 | Kenneth Biba
* **Milestone:** 
  * Integrity rules for state machine architectures
  * [Integrity Considerations for Secure Computer Systems (DTIC)](https://apps.dtic.mil/sti/citations/ADA039324)
* **Paradigm Shift:** 
  * Formulated the mathematical inverse of Bell LaPadula to address system state integrity rather than secrecy
  * [Biba Integrity Model](https://en.wikipedia.org/wiki/Biba_Model)
* **Core Rule:** Mathematical integrity enforcement
  * Simple Integrity Property prohibiting reading down
  * Star Integrity Property prohibiting writing up

### 1977 | [Ron Rivest](https://en.wikipedia.org/wiki/Ron_Rivest), [Adi Shamir](https://en.wikipedia.org/wiki/Adi_Shamir) and [Leonard Adleman](https://en.wikipedia.org/wiki/Leonard_Adleman)
* **Milestone:** 
  * Practical public key ciphers and digital signatures
  * [A Method for Obtaining Digital Signatures and Public Key Cryptosystems (ACM)](https://dl.acm.org/doi/10.1145/359340.359342)
* **Paradigm Shift:** Public asymmetric encryption and signature validation
  * [The RSA Cryptosystem](https://en.wikipedia.org/wiki/RSA)
  * RSA security is associated with the difficulty of factoring large semiprime numbers, though RSA inversion is not known to be equivalent to factoring

### 1984 | [Ken Thompson](https://en.wikipedia.org/wiki/Ken_Thompson)
* **Milestone:** 
  * ACM Turing Award lecture on untrusted computing bases
  * [Reflections on Trusting Trust (ACM)](https://dl.acm.org/doi/10.1145/358198.358210)
* **Paradigm Shift:** Demonstrated how a compiler can insert a backdoor into programs it builds and reproduce that behavior when compiling a future version of itself, even when the backdoor is absent from the reviewed source code
* **Lineage:** Reviewing application source code alone may not be enough to verify the software we run
  * The example remains relevant to compiler security, software provenance and supply chain assurance
  * It shows why trust in build tools and compiler chains also matters

### 1986 | [Dorothy Denning](https://en.wikipedia.org/wiki/Dorothy_E._Denning)
* **Milestone:** 
  * Behavioral audit and anomaly modeling
  * [An Intrusion Detection Model (IEEE)](https://ieeexplore.ieee.org/document/1702202)
* **Paradigm Shift:** Formulated the first formal architecture for behavioral anomaly detection and rule based audit monitoring
  * Formed the architectural foundation for modern [Intrusion Detection Systems](https://en.wikipedia.org/wiki/Intrusion_detection_system)
  * Researched and refined during Denning's tenure at George Mason University in Virginia

---

## 3. Web and Network Infrastructure Revolution (Late 1980s to Early 2000s)

### 1986 | [Cliff Stoll](https://en.wikipedia.org/wiki/Clifford_Stoll)
* **Milestone:** Cyber forensic accounting and decoy systems documented in [The Cuckoo's Egg](https://en.wikipedia.org/wiki/The_Cuckoo%27s_Egg_(book))
* **Paradigm Shift:** 
  * Tracked KGB contracted hackers traversing ARPANET and Milnet by investigating 75 cent accounting discrepancies
  * Stoll pioneered real time audit tracing, honeytokens and decoy documents

### 1988 | [Robert Tappan Morris](https://en.wikipedia.org/wiki/Robert_Tappan_Morris)
* **Milestone:** First widespread network propagation exploit
  * [The Morris Worm](https://en.wikipedia.org/wiki/Morris_worm)
  * [Technical Analysis by Spafford (Purdue)](https://spaf.cerias.purdue.edu/tech-reps/823.pdf)
* **Paradigm Shift:** 
  * Exploited buffer overflows in fingerd, debug modes in sendmail and weak trust relationships across network services
  * Prompted the formation of DARPA's [CERT Coordination Center](https://www.sei.cmu.edu/about/divisions/cert/)

### 1991 | [Phil Zimmermann](https://en.wikipedia.org/wiki/Phil_Zimmermann)
* **Milestone:** Zimmermann created [Pretty Good Privacy](https://en.wikipedia.org/wiki/Pretty_Good_Privacy) to bring public key encryption directly to end users
* **Paradigm Shift:** 
  * Distributed military grade public key encryption directly to end consumers
  * Contributed to public debate and legal disputes over cryptography exports
  * It was one part of a broader history and did not alone end United States export restrictions
  * Its distribution made public key encryption available directly to end users

### 1985 | [Taher Elgamal](https://en.wikipedia.org/wiki/Taher_Elgamal)
* **Milestone:** ElGamal introduced a public key cryptosystem
  * [The ElGamal Cryptosystem](https://ieeexplore.ieee.org/document/1057074)
  * The scheme is a separate development from SSL and TLS

### 1994 to 1999 | SSL and the development of TLS
* **Milestone:** Netscape developed Secure Sockets Layer to protect web communications. The IETF later standardized Transport Layer Security as its successor
  * [RFC 2246: TLS 1.0](https://www.rfc-editor.org/rfc/rfc2246)
  * [RFC 8446: TLS 1.3](https://www.rfc-editor.org/rfc/rfc8446)
* **Paradigm Shift:** Web transport security combined authenticated key exchange, encryption and integrity protection

### 1994 to 1998 | [Nir Zuk](https://en.wikipedia.org/wiki/Palo_Alto_Networks#History) and [Marcus Ranum](https://en.wikipedia.org/wiki/Marcus_J._Ranum)
* **Milestone:** 
  * Network traffic isolation and packet state inspection
  * [Stateful Packet Inspection Overview](https://en.wikipedia.org/wiki/Stateful_firewall)
* **Paradigm Shift:** Filtering network streams by context
  * Ranum is associated with application level proxy filtering
  * Historical accounts associate Zuk with stateful inspection work at Check Point and later next generation firewall development
  * Attribute specific inventions and dates only where the cited source supports them
  * Keep later next generation firewall developments separate from the early history of stateful inspection

---

## 4. Internet Scale Security and Software Supply Chains (2000s to 2020s)

### 2000s to Present | Cloud services, identity and ransomware
* **Milestone:** Security practice expanded as organizations moved services, identities and data onto internet connected platforms
* **Paradigm Shift:** Authentication, access control, patching, backups and incident response became central to protecting distributed systems
  * [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
  * [CISA Ransomware Guidance](https://www.cisa.gov/stopransomware)

### 2010 | Stuxnet and industrial control systems
* **Milestone:** Stuxnet brought wider attention to the security of industrial control systems and the connection between digital operations and physical processes
* **Paradigm Shift:** Systems that control physical processes need careful separation, monitoring and recovery planning
  * [CISA Industrial Control Systems](https://www.cisa.gov/topics/industrial-control-systems)
  * [NIST Guide to Operational Technology Security](https://csrc.nist.gov/pubs/sp/800/82/r3/final)

### 2020 | SolarWinds supply chain compromise
* **Milestone:** A compromise of a software build and update process affected downstream organizations
* **Paradigm Shift:** Trust in software suppliers and update channels creates shared risk across many customers
  * [CISA SolarWinds Alert](https://www.cisa.gov/news-events/alerts/2020/12/17/advanced-persistent-threat-compromises-government-agencies-critical-infrastructure-and-private-sector)
  * [NIST Secure Software Development Framework](https://csrc.nist.gov/pubs/sp/800/218/final)

---

## 5. Mobile, Social Web and Zero Trust (Mid 2000s to 2010s)

### 2005 | [Samy Kamkar](https://en.wikipedia.org/wiki/Samy_Kamkar)
* **Milestone:** 
  * Self propagating client side web worms
  * [The Samy Worm](https://en.wikipedia.org/wiki/Samy_(computer_worm))
* **Paradigm Shift:** 
  * Demonstrated weaponized document object model manipulation and cross site scripting
  * Proved that client side browser scripts could host autonomous and exponentially replicating payloads

### 2008 | [Dan Kaminsky](https://en.wikipedia.org/wiki/Dan_Kaminsky)
* **Milestone:** 
  * Global DNS cache manipulation vulnerability
  * [Kaminsky DNS Vulnerability](https://en.wikipedia.org/wiki/Dan_Kaminsky#DNS_flaw)
* **Paradigm Shift:** 
  * Identified structural entropy flaws in DNS transaction identifiers and source port selection that enabled blind recursive cache poisoning
  * Kaminsky coordinated the first secret, cross industry global emergency patch operation

### 2010 to 2020 | Zero Trust Architecture
* **Milestone:** John Kindervag helped popularize the Zero Trust concept in 2010. NIST published its Zero Trust Architecture guidance as SP 800-207 in 2020
  * [NIST SP 800-207: Zero Trust Architecture](https://csrc.nist.gov/pubs/sp/800/207/final)
  * [Zero Trust Architecture Overview](https://en.wikipedia.org/wiki/Zero_trust_architecture)
* **Paradigm Shift:** Zero Trust shifts security decisions toward explicit authentication and authorization, least privilege and ongoing evaluation of access
  * It is an architectural approach, not a single product
  * It does not guarantee security on its own
  * It supplements perimeter controls rather than making network boundaries irrelevant

### 2013 | [Moxie Marlinspike](https://en.wikipedia.org/wiki/Moxie_Marlinspike) and Trevor Perrin
* **Milestone:** 
  * Real time session key rotation
  * [The Double Ratchet Algorithm Specification (Signal)](https://signal.org/docs/specifications/doubleratchet/)
  * [Signal: Advanced Ratcheting](https://signal.org/blog/advanced-ratcheting/)
* **Paradigm Shift:** The Double Ratchet derives fresh message keys as communication continues
  * Its design aims to provide forward security and recovery after some key compromises, subject to the protocol's assumptions and continued use
  * The security properties depend on how the protocol is implemented and used

---

## 6. Adversarial Machine Learning and AI Security (2014 to Present)

### 2014 | [Ian Goodfellow](https://en.wikipedia.org/wiki/Ian_Goodfellow)
* **Milestone:** 
  * Neural network manipulation via gradient exploitation
  * [Explaining and Harnessing Adversarial Examples (arXiv)](https://arxiv.org/abs/1412.6572)
* **Paradigm Shift:** The paper introduced the Fast Gradient Sign Method and studied how small, deliberately chosen input changes can affect classifier predictions
  * The authors proposed an explanation based on the behavior of models in high dimensional spaces
  * The result does not establish that every model fails in the same way

### 2016 to 2018 | Nicolas Papernot, [Dawn Song](https://en.wikipedia.org/wiki/Dawn_Song) and other machine learning security researchers
* **Milestone:** Researchers studied black box attack models and privacy preserving machine learning
  * [Towards the Science of Security and Privacy in Machine Learning (IEEE)](https://ieeexplore.ieee.org/document/8418594)
  * [Private Aggregation of Teacher Ensembles PATE (arXiv)](https://arxiv.org/abs/1610.05755)
* **Paradigm Shift:** This work mapped several attack surfaces and privacy questions for machine learning systems
  * Describe each result alongside its authors and the specific guarantee or attack it studies
  * Differential privacy guarantees depend on the defined data, mechanism and privacy parameters
  * PATE provides privacy guarantees for aggregated teacher predictions under stated assumptions, not a general guarantee for model parameters

### 2021 | Florian Tramèr, [Nicholas Carlini](https://en.wikipedia.org/wiki/Nicholas_Carlini) and coauthors
* **Milestone:** Researchers demonstrated methods for extracting some memorized training examples from language models in [Extracting Training Data from Large Language Models](https://www.usenix.org/conference/usenixsecurity21/presentation/carlini-extracting)
* **Paradigm Shift:** Training data exposure depends on the model, the data and the extraction method. The paper demonstrates a risk, not that all models reveal their training data

### 2023 | Andy Zou and coauthors
* **Milestone:** Researchers described transferable adversarial suffixes that could bypass safeguards in some aligned language models in [Universal and Transferable Adversarial Attacks on Aligned Language Models](https://arxiv.org/abs/2307.15043)
* **Paradigm Shift:** Safety testing should include adaptive attacks and describe the systems and conditions actually evaluated

### 2025 | AI security engineering
* **Milestone:** NIST published draft guidance on cybersecurity and artificial intelligence risks
  * [NIST Cyber AI Profile](https://csrc.nist.gov/pubs/ir/8596/iprd)
  * [NIST Secure Software Development Practices for Generative AI](https://csrc.nist.gov/pubs/sp/800/218/a/final)
* **Paradigm Shift:** AI security includes protecting AI systems from attacks and using AI tools securely in software development
  * The Cyber AI Profile is a draft and may change
  * NIST's secure development guidance for generative AI is a separate final publication

---

## 7. Quantum Cybersecurity and Post Quantum Cryptography

### 1984 to 1991 | Charles Bennett, [Gilles Brassard](https://en.wikipedia.org/wiki/Gilles_Brassard) and [Artur Ekert](https://en.wikipedia.org/wiki/Artur_Ekert)
* **Milestone:** Quantum physical key distribution protocols
  * [BB84 Protocol (Theoretical Computer Science)](https://doi.org/10.1016/j.tcs.2014.05.025)
  * [E91 Entanglement Protocol (Physical Review Letters)](https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.67.661)
* **Paradigm Shift:** BB84 uses nonorthogonal quantum states to detect certain kinds of eavesdropping and does not require entanglement
  * E91 is a separate protocol that uses entangled pairs
  * Quantum key distribution also depends on implementation, authentication and the security of the surrounding system

### 1994 | [Peter Shor](https://en.wikipedia.org/wiki/Peter_Shor)
* **Milestone:** 
  * Polynomial time quantum period finding
  * [Polynomial-Time Algorithms for Prime Factorization and Discrete Logarithms on a Quantum Computer (SIAM)](https://epubs.siam.org/doi/10.1137/S0097539795293172)
* **Paradigm Shift:** 
  * Formulated a polynomial time quantum algorithm for prime factorization and discrete logarithms
  * The algorithm would threaten RSA, DSA and elliptic curve cryptography if run on a sufficiently large fault tolerant quantum computer
  * Such a cryptographically relevant machine is not currently available

### 2005 to Present | [Oded Regev](https://en.wikipedia.org/wiki/Oded_Regev_(computer_scientist)) and Chris Peikert
* **Milestone:** Hard problems over geometric vector lattices
  * [On Lattices, Learning with Errors, Random Linear Codes and Cryptography (ACM)](https://dl.acm.org/doi/10.1145/1060590.1060603)
  * [Lattice Cryptography Survey (Peikert)](https://web.eecs.umich.edu/~cpeikert/pubs/suite.pdf)
* **Paradigm Shift:** 
  * Introduced worst case to average case reductions based on geometric lattice problems
  * This mathematics established the theoretical engine for practical quantum resistant encryption

### 2016 to 2024 | Dustin Moody
* **Milestone:** Standardizing global post quantum cryptography algorithms
  * [NIST Post Quantum Cryptography Standardization Project](https://csrc.nist.gov/projects/post-quantum-cryptography)
  * Managed out of the National Institute of Standards and Technology in Gaithersburg, Maryland
* **Paradigm Shift:** Finalized modern quantum resistant cryptographic standards
  * [FIPS 203 ML KEM Module Lattice Key Encapsulation](https://csrc.nist.gov/pubs/fips/203/final)
  * [FIPS 204 ML DSA Module Lattice Digital Signatures](https://csrc.nist.gov/pubs/fips/204/final)
  * [FIPS 205 SLH DSA Stateless Hash Digital Signatures](https://csrc.nist.gov/pubs/fips/205/final)

---

## 8. Bio Hybrid Computing, Organoid Intelligence and Cyberbiosecurity

This section describes an emerging research area. The entries distinguish demonstrated experiments from proposed future risks.

### 2018 | Randall Murch and coauthors
* **Milestone:** The paper described cyberbiosecurity as an emerging field
  * [Cyberbiosecurity: An Emerging New Discipline to Help Safeguard the Advanced Life Sciences (Frontiers)](https://www.frontiersin.org/journals/bioengineering-and-biotechnology/articles/10.3389/fbioe.2018.00039/full)
  * Murch was affiliated with Virginia Tech in Blacksburg, Virginia
* **Paradigm Shift:** The paper identified risks where automated computational workflows interface with physical biology
  * It discussed automated gene synthesis pipelines and biofoundry control systems
  * Distinguish cyberbiosecurity risks from research that encodes digital malware in synthetic DNA
  * Treat specific attack scenarios as hypotheses unless a source documents a demonstration

### 2022 | Brett Kagan and coauthors
* **Milestone:** 
  * In vitro closed loop neural gameplay
  * [In vitro neurons learn and exhibit sentience when embodied in a simulated game world (Neuron)](https://www.cell.com/neuron/fulltext/S0896-6273(22)00806-6)
* **Paradigm Shift:** The DishBrain team connected cultured human and rodent cortical neurons to a simulated game through high density microelectrode arrays
  * The experiment demonstrated a closed loop interaction between cells and a simulated environment
  * It did not establish that the system was sentient
  * Security implications for future systems remain an open research topic

### 2023 | Thomas Hartung and coauthors
* **Milestone:** Researchers proposed organoid intelligence as a possible future area of biocomputing research using three dimensional human brain organoids
  * [Organoid intelligence (OI): the new frontier in biocomputing and intelligence in a dish (Frontiers)](https://www.frontiersin.org/journals/science/articles/10.3389/fsci.2023.1017235/full)
  * The paper outlines a research direction rather than a deployed computing platform
  * The work was led by researchers at Johns Hopkins University
* **Paradigm Shift:** Future systems could raise questions about data protection, system integrity and laboratory safety
  * The paper does not establish operational security frameworks or demonstrated attacks
  * Treat proposed memory and security mechanisms as research questions

### Emerging Threat Vectors: Bio Silicon and Neurosecurity
These are proposed areas for further study. The examples below are threat hypotheses and should not be read as demonstrated attacks
* **Electrophysiological Signal Spoofing:** Study whether electrical inputs could alter system behavior in future bio hybrid platforms
  * [Cognitive Security and Brain Data Privacy Frameworks](https://link.springer.com/article/10.1007/s12152-021-09468-8)
  * Claims about manipulating biological memory require direct experimental evidence
* **Wetware Operational Technology Exploits:** Assess risks to automated microfluidic life support systems, perfusion loops and environmental controls
* **Neural Reconstruction and Privacy Inversion:** Study what can be inferred from organoid activity data and donor genomic metadata
