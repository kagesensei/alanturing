# Alan Turing: A Tribute in Code
As a Cybersecurity Data Scientist I decided it's overdue to start sharing code publicly to showcase my skills. I decided to start with looking at the work of Alan Turing.  As a child, I was captivated by the genius of Alan Turing—his groundbreaking work in cryptanalysis, his vision of machine intelligence, and his profound contributions to modern computing. The Turing Test sparked my early curiosity about artificial intelligence, while his role in breaking the Enigma cipher showed me the power of mathematical logic in the real world.

This repository is a proof of concept for his work, a homage to the man who laid the foundation for modern computing and cybersecurity. It will feature Python implementations of:

- Turing Machine concepts, including a Universal Turing Machine.

- Cryptanalysis algorithms, from frequency analysis to Enigma decryption.

- Simulations of historical devices, such as the Bombe and the Enigma machine.

By recreating and exploring these systems, I hope to keep Turing’s legacy alive—both as a pioneer of theoretical computer science and as a hero of World War II.

For those who wish to understand computation from its origins, this repository is both a study and a tribute.

## Setup

Requires Python 3.12. Create and activate a virtual environment at the repo
root before running anything:

```
py -3.12 -m venv .venv

# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# Windows (Git Bash)
source .venv/Scripts/activate

# macOS/Linux
source .venv/bin/activate
```

Each project folder is self-contained (standard library only so far) — with
the venv active, `cd` into a project directory and run its script or
`python -m unittest -v` directly.

## Hugging Face

Any models, datasets, or spaces published from this project are tracked in
[HUGGINGFACE.md](HUGGINGFACE.md).

## Roadmap

### Turing Machine Concepts
- [x] [Basic Turing Machine Simulator](turing_machines/basic_simulator)
- [x] [Universal Turing Machine](turing_machines/universal_turing_machine)
- [x] [Non-Deterministic Turing Machine Simulation](turing_machines/nondeterministic_turing_machine)
- [x] [Turing Machine for Arithmetic](turing_machines/arithmetic_turing_machine)
- [x] [Turing Machine for Palindrome Checking](turing_machines/palindrome_turing_machine)
- [x] [Self-Replicating Turing Machine](turing_machines/self_replicating_turing_machine)

### Cryptanalysis & Enigma
- [x] [Enigma Machine Simulator](cryptanalysis/enigma_simulator)
- [x] [Brute Force Enigma Cracker](cryptanalysis/brute_force_cracker)
- [x] [Statistical Frequency Analysis for Cryptanalysis](cryptanalysis/frequency_analysis)
- [x] [Simulated Bombe Machine](cryptanalysis/bombe_simulator)
- [x] [Automated Enigma Key Discovery](cryptanalysis/automated_key_discovery)
- [ ] Lorenz Cipher Simulator & Cracker

### Advanced Concepts
- [ ] Quantum-Inspired Cryptanalysis
- [ ] Turing-Complete Cellular Automaton
- [ ] Genetic Algorithm for Code Breaking

### Bonus Projects & Reflections
- [ ] Turing Test Simulator (simple chat-based exploration of the Turing Test)
- [ ] Interactive Enigma GUI (desktop or web front-end for the Enigma simulator)
- [ ] `historical_notes.md` — personal reflections and inspirations behind this project
