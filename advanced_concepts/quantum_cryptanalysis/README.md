# Quantum-Inspired Cryptanalysis

Both sides of the quantum/cryptography story: **offense** — genuine
(small-scale) quantum algorithm simulations showing why a large enough
quantum computer threatens classical cryptography — and **defense** —
the NIST post-quantum standards designed to resist that threat.

Requires Python 3.12 — see the [repo root README](../../README.md#setup)
for venv setup, then:

```
pip install -r requirements.txt
```

## Offense: Shor's and Grover's algorithms

- **`qsim.py`** — a minimal pure-Python quantum statevector simulator
  (Hadamard, controlled-phase, a reversible classical-function gate, a
  Grover phase-flip oracle, diffusion, and an exact Quantum Fourier
  Transform computed directly from its mathematical definition). Every
  gate is verified independently — the QFT is checked against a
  from-scratch reference DFT implementation, not just trusted.
- **`shors_algorithm.py`** — Shor's algorithm: classical pre/post-
  processing (coprime base selection, continued fractions, gcd) wrapped
  around genuine quantum period-finding built on `qsim.py`. Factors
  small numbers (demonstrated: 15, 21) — simulating a full statevector
  costs `O(2**n_qubits)`, so this is the honest limit of "quantum-
  inspired" without real quantum hardware.
- **`grovers_algorithm.py`** — Grover's search: `O(sqrt(N))` queries to
  find a marked item versus `O(N)` classically. Directly relevant to
  symmetric-key cryptanalysis — a quantum computer running this against
  an n-bit keyspace (an Enigma-style key search, a block cipher) needs
  only `sqrt(2**n)` tries, which is why NIST recommends doubling
  symmetric key lengths for post-quantum security.
- **`qiskit_backend.py`** / **`cirq_backend.py`** — the same Grover's
  search, rebuilt on real Qiskit (IBM) and Cirq (Google) instead of the
  hand-rolled simulator, exposing an equivalent API for direct
  comparison. **Named `*_backend.py`, not `qiskit.py`/`cirq.py`**: a
  module in this folder literally named `qiskit.py` would shadow the
  real `qiskit` package for its own `from qiskit import ...` line (and
  for every other file here) — Python resolves same-directory modules
  before installed packages. Shor's algorithm isn't reimplemented in
  either backend: modern Qiskit dropped its bundled Shor's primitive, so
  a "real" version would mean hand-building the identical modular-
  exponentiation-plus-QFT circuit already built in `shors_algorithm.py`,
  just on a different substrate — duplicated engineering, no new
  content. Grover's is the circuit shape these frameworks are actually
  built to express directly, so it's the meaningful comparison.

## Defense: FIPS 203/204/205

- **`pqc.py`** — a small, consistent API for the three finalized NIST
  post-quantum standards: **FIPS 203 (ML-KEM)** key encapsulation,
  **FIPS 204 (ML-DSA)** signatures, and **FIPS 205 (SLH-DSA, built on
  SPHINCS+)** signatures. None of these are implemented from scratch —
  lattice- and hash-based cryptography is genuinely dangerous to
  hand-roll without extensive review — this wraps
  [`quantcrypt`](https://pypi.org/project/quantcrypt/), a maintained
  Python binding for the PQClean reference implementations.

## Usage

```python
from shors_algorithm import factor
from grovers_algorithm import grover_search
from pqc import ml_kem_keygen, ml_kem_encapsulate, ml_kem_decapsulate

result = factor(15)
print(result.factors)  # (3, 5)

search = grover_search(num_qubits=6, marked_indices=(41,))
print(search.marked_index, search.success_probability)

keys = ml_kem_keygen()
encapsulation = ml_kem_encapsulate(keys.public_key)
assert ml_kem_decapsulate(keys.secret_key, encapsulation.ciphertext) == encapsulation.shared_secret
```

Run any module's built-in demo directly, e.g. `python shors_algorithm.py`,
`python qiskit_backend.py`, `python pqc.py`.

## Performance notes

- Shor's period-finding costs roughly `O(2**(2*n_count))` for the QFT
  step; factoring 15 takes well under a second, 21 takes several
  seconds. Larger toy numbers (e.g. 35) are correspondingly slower and
  are not included in the automated test suite for that reason.
- The counting register size is the tight bound (`2**n_count >= N**2`),
  not the more commonly quoted but more generous `2 * bit_length(N)` —
  cut runtime roughly 4x for N=21 with no loss of correctness.

## Tests

```
python -m unittest -v
```

50 tests across all six modules. The QFT is checked against an
independent reference DFT implementation; Grover's iteration count is
checked against the exact textbook N=4 case (where the commonly quoted
approximate formula is actually wrong); Shor's is checked against known
factorizations across multiple random seeds; the PQC wrapper is checked
for correct round-trips and correct rejection of tampered
messages/wrong keys.
