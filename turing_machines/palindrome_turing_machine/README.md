# Turing Machine for Palindrome Checking

A single-tape Turing Machine that decides whether a binary string reads
the same forwards and backwards, using the classic outside-in
construction: compare the leftmost remaining symbol against the
rightmost remaining symbol, mark both consumed on a match, and repeat.
Any mismatch rejects immediately; running out of symbols to compare
(with none left, or exactly one middle symbol left over) means every
pair matched, so the machine accepts.

Requires Python 3.12 — see the [repo root README](../../README.md#setup) for
venv setup.

## How it decides

Consumed cells are overwritten with the marker `#` (not blanked), so on
every pass the machine can tell "a symbol I already matched" apart from
"the true end of the tape" while it walks back and forth:

1. From the leftmost unconsumed cell: if it's blank, every symbol has
   been matched off in pairs — **accept**.
2. Otherwise mark it `#` and remember its value, then walk right to the
   current rightmost unconsumed cell.
3. If there's nothing left to walk to, the marked symbol was the lone
   middle character of an odd-length string — **accept**.
4. Otherwise compare: a match marks that symbol `#` too and the head
   walks all the way back to the start for the next round; a mismatch
   has no further transition, so the machine halts without ever
   reaching its accept state — **reject**.

## Usage

```python
from palindrome_turing_machine import PalindromeTuringMachine

checker = PalindromeTuringMachine()
result = checker.check("10101")
print(result.is_palindrome)  # True
print(result.steps)          # how many transitions it took

result = checker.check("10100")
print(result.is_palindrome)  # False
```

Run the built-in demo:

```
python palindrome_turing_machine.py
```

## Tests

```
python -m unittest -v
```

Covers empty/single-character strings, even- and odd-length palindromes
and non-palindromes, a mismatch confined to the outermost pair, and an
exhaustive check of every binary string up to length 8 (511 strings),
each verified against Python's own `s == s[::-1]`.
