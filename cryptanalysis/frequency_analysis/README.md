# Statistical Frequency Analysis for Cryptanalysis

Letter-frequency-based cryptanalysis of monoalphabetic substitution
ciphers: a chi-squared goodness-of-fit score against reference English
letter frequencies, a full brute-force break for shift (Caesar) ciphers,
and a frequency-rank heuristic for general substitution ciphers.

Requires Python 3.12 — see the [repo root README](../../README.md#setup) for
venv setup.

## Usage

```python
from frequency_analysis import crack_caesar_cipher, frequency_substitution_guess

result = crack_caesar_cipher(ciphertext)
print(result.shift, result.plaintext)

# For a general (non-shift) substitution cipher, frequency ranking alone
# gives a good first-pass guess, not a guaranteed exact break:
guess = frequency_substitution_guess(ciphertext)
```

Run the built-in demo:

```
python frequency_analysis.py
```

## Scope

- `crack_caesar_cipher` is a full, exact break: it tries all 26 shifts and
  picks the one whose decryption's letter distribution best matches
  English. This always finds the correct shift given enough ciphertext.
- `frequency_substitution_guess` handles the general case (an arbitrary
  letter-for-letter substitution, not just a shift). Matching frequency
  *rank* alone is the classic first pass real cryptanalysts use, but it
  isn't guaranteed to recover an arbitrary substitution exactly — real
  English text doesn't perfectly follow the idealized reference
  distribution, and short ciphertexts especially can throw the ranking
  off. Historically, this guess is then refined by hand using word
  patterns and context, which is out of scope here.

## Tests

```
python -m unittest -v
```
