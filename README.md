# Alan Turing: A Tribute in Code
As a Cybersecurity Data Scientist I decided it's overdue to start sharing code publicly to showcase my skills. I decided to start with looking at the work of Alan Turing.  As a child, I was captivated by the genius of Alan Turing—his groundbreaking work in cryptanalysis, his vision of machine intelligence, and his profound contributions to modern computing. The Turing Test sparked my early curiosity about artificial intelligence, while his role in breaking the Enigma cipher showed me the power of mathematical logic in the real world.

This repository is a working educational collection, a homage to the man who laid the foundation for modern computing and cybersecurity. It includes Python implementations of:

- Turing Machine concepts, including a Universal Turing Machine.

- Cryptanalysis algorithms, from frequency analysis to Enigma decryption.

- Simulations of historical devices, such as the Bombe and the Enigma machine.

By recreating and exploring these systems, I hope to keep Turing’s legacy alive—both as a pioneer of theoretical computer science and as a hero of World War II.

For those who wish to understand computation from its origins, this repository is both a study and a tribute.

## Start here

All 18 main roadmap items have implementations, including the local Turing Test
Simulator. Its configurable model connection is ready for a future turing-a1
model; the default demo does not impersonate a trained model. Each implementation
has tests, a runnable example, and its own README.

| Explore | Run from the root after setup | What to look for |
| --- | --- | --- |
| Computation | `python turing_machines/basic_simulator/turing_machine.py` | Binary increment and complement through tape transitions |
| Cryptanalysis | `python cryptanalysis/automated_key_discovery/automated_key_discovery.py` | Rotor and plugboard recovery with `fully_verified=True` |
| Self-replication | `python turing_machines/self_replicating_turing_machine/self_replicating_turing_machine.py` | A 1,280-bit description copied in 4,922,883 machine steps |
| Quantum concepts | `python advanced_concepts/quantum_cryptanalysis/shors_algorithm.py` | Toy factoring with reported quantum/classical paths |
| Interactive Enigma | `python bonus/enigma_gui/app.py` | Open `http://127.0.0.1:5000` to configure the machine and watch rotor positions |
| The imitation room | `python bonus/turing_test_simulator/app.py` | Open `http://127.0.0.1:5001` for evidence-aware chat and a blind comparison |

For example, the key-discovery demo reports:

```text
rotors=('III', 'V', 'I') start=('Q', 'E', 'L')
plugboard_pairs=(('B', 'Z'), ('H', 'Y'), ('K', 'P'), ('Q', 'X'))
fully_verified=True
```

These are bounded educational implementations. Enigma search assumes known
ring settings; Lorenz recovery assumes known plaintext and other key material;
quantum statevectors only support small demonstrations. The genetic codebreaker
works on its demo but underperforms frequency analysis on the current
[held-out benchmark](advanced_concepts/genetic_codebreaker/BENCHMARK.md).

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

On macOS/Linux, create the environment with `python3.12 -m venv .venv`.

Each project folder is self-contained (standard library only, except a
few app-style projects like `bonus/enigma_gui` that pin their own extra
dependencies in a project-local `requirements.txt`) — with the venv
active, `cd` into a project directory, `pip install -r requirements.txt`
if one's present, and run its script or `python -m unittest -v` directly.

## Verify the collection

For all existing project tests, install the development tools and optional
runtime backends in the activated environment:

```text
python -m pip install -r requirements-dev.txt -r bonus/enigma_gui/requirements.txt -r bonus/turing_test_simulator/requirements.txt -r advanced_concepts/quantum_cryptanalysis/requirements.txt
python -m unittest discover -v
python tools/run_lint.py
```

Root discovery runs each project's actual tests in a separate interpreter.
The final count is the number of project suites; each suite also prints its
individual test count. Missing dependencies and skipped tests fail the check.
The [CI workflow](.github/workflows/checks.yml) runs tests and lint on Linux
and Windows. See [tools/README.md](tools/README.md) for the reviewed lint policy.

To reproduce the slower cryptanalysis experiment separately:

```text
python advanced_concepts/genetic_codebreaker/benchmark.py
```

## Hugging Face

Any models, datasets, or spaces published from this project are tracked in
[HUGGINGFACE.md](HUGGINGFACE.md).

The [turing-a1 training workflow](finetune) now lives here as a separate
directory: deterministic domain examples, disjoint evaluation splits, a 3B
QLoRA configuration, and local serving/evaluation scripts. Data preparation and
contract tests run locally; GPU training and publication have not run. The
historical persona remains an optional application layer.

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
- [x] [Lorenz Cipher Simulator & Cracker](cryptanalysis/lorenz_cipher)

### Advanced Concepts
- [x] [Quantum-Inspired Cryptanalysis](advanced_concepts/quantum_cryptanalysis)
- [x] [Turing-Complete Cellular Automaton](advanced_concepts/cellular_automaton)
- [x] [Genetic Algorithm for Code Breaking](advanced_concepts/genetic_codebreaker)

### Bonus Projects & Reflections
- [x] [Turing Test Simulator](bonus/turing_test_simulator) — local chat, evidence-scoped personas, human/model comparison, and configurable model endpoint; turing-a1 training remains separate work
  - [x] Groundwork: [Alan Turing evidence-based historical persona](persona/alan_turing) — provenance/confidence-tagged source-of-truth data (not the simulator itself)
- [x] [Interactive Enigma GUI](bonus/enigma_gui) (Flask web front-end for the Enigma simulator)
- [x] [`historical_notes.md`](historical_notes.md) — personal reflections and inspirations behind this project
