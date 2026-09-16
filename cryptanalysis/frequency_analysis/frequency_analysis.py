"""Statistical letter-frequency analysis for cryptanalysis: a chi-squared
goodness-of-fit score against reference English letter frequencies, used
to break monoalphabetic substitution ciphers -- a full brute-force break
for shift (Caesar) ciphers, and a frequency-rank heuristic for general
substitution.
"""

from __future__ import annotations

from dataclasses import dataclass

ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
ALPHABET_SIZE = len(ALPHABET)

# Standard published English letter frequencies (percent of all letters),
# from corpus analysis commonly cited as the reference table for classical
# cryptanalysis (e.g. Lewand's "Cryptological Mathematics").
ENGLISH_LETTER_FREQUENCIES: dict[str, float] = {
    "E": 12.702, "T": 9.056, "A": 8.167, "O": 7.507, "I": 6.966,
    "N": 6.749, "S": 6.327, "H": 6.094, "R": 5.987, "D": 4.253,
    "L": 4.025, "C": 2.782, "U": 2.758, "M": 2.406, "W": 2.360,
    "F": 2.228, "G": 2.015, "Y": 1.974, "P": 1.929, "B": 1.492,
    "V": 0.978, "K": 0.772, "J": 0.153, "X": 0.150, "Q": 0.095,
    "Z": 0.074,
}


def _only_letters(text: str) -> str:
    return "".join(char for char in text.upper() if char in ALPHABET)


def letter_counts(text: str) -> dict[str, int]:
    letters = _only_letters(text)
    return {letter: letters.count(letter) for letter in ALPHABET}


def letter_frequencies(text: str) -> dict[str, float]:
    """Each letter's share of the text's A-Z letters, as a percentage."""
    counts = letter_counts(text)
    total = sum(counts.values())
    if not total:
        raise ValueError("text must contain at least one A-Z letter")
    return {letter: 100.0 * count / total for letter, count in counts.items()}


def chi_squared_statistic(text: str) -> float:
    """Chi-squared goodness-of-fit between `text`'s letter distribution and
    ENGLISH_LETTER_FREQUENCIES. Lower means text looks more like English.
    """
    counts = letter_counts(text)
    total = sum(counts.values())
    if not total:
        raise ValueError("text must contain at least one A-Z letter")
    statistic = 0.0
    for letter in ALPHABET:
        expected = ENGLISH_LETTER_FREQUENCIES[letter] / 100.0 * total
        observed = counts[letter]
        statistic += (observed - expected) ** 2 / expected
    return statistic


def caesar_encrypt(plaintext: str, shift: int) -> str:
    return "".join(
        ALPHABET[(ALPHABET.index(char) + shift) % ALPHABET_SIZE] if char in ALPHABET else char
        for char in plaintext.upper()
    )


def caesar_decrypt(ciphertext: str, shift: int) -> str:
    return caesar_encrypt(ciphertext, -shift)


@dataclass
class CaesarCrackResult:
    shift: int
    plaintext: str
    chi_squared: float


def crack_caesar_cipher(ciphertext: str) -> CaesarCrackResult:
    """Try all 26 shifts and return the one whose decryption's letter
    distribution best matches English (lowest chi-squared statistic).
    """
    if not _only_letters(ciphertext):
        raise ValueError("ciphertext must contain at least one A-Z letter")

    best: CaesarCrackResult | None = None
    for shift in range(ALPHABET_SIZE):
        candidate_plaintext = caesar_decrypt(ciphertext, shift)
        score = chi_squared_statistic(candidate_plaintext)
        if best is None or score < best.chi_squared:
            best = CaesarCrackResult(shift, candidate_plaintext, score)
    return best


def frequency_substitution_guess(ciphertext: str) -> str:
    """Heuristic monoalphabetic-substitution break: map the ciphertext's
    most frequent letters onto English's most frequent letters.

    A classic first-pass cryptanalysis technique -- exact for a shift
    cipher on a long enough sample, and a reasonable starting point for a
    general substitution, but not guaranteed to fully recover an arbitrary
    substitution from frequency alone (real cryptanalysis then refines the
    guess by hand using word patterns and context).
    """
    counts = letter_counts(ciphertext)
    if not sum(counts.values()):
        raise ValueError("ciphertext must contain at least one A-Z letter")

    cipher_ranked = sorted(ALPHABET, key=lambda letter: (-counts[letter], letter))
    english_ranked = sorted(
        ALPHABET, key=lambda letter: (-ENGLISH_LETTER_FREQUENCIES[letter], letter)
    )
    mapping = dict(zip(cipher_ranked, english_ranked))
    return "".join(mapping[char] if char in ALPHABET else char for char in ciphertext.upper())


if __name__ == "__main__":
    secret_shift = 11
    original_message = (
        "TURING BROKE THE ENIGMA CODE AT BLETCHLEY PARK AND HELPED WIN THE WAR "
        "BY BUILDING MACHINES THAT COULD THINK FASTER THAN ANY HUMAN CODEBREAKER"
    )
    encrypted_message = caesar_encrypt(original_message, secret_shift)
    print(f"ciphertext: {encrypted_message}")

    result = crack_caesar_cipher(encrypted_message)
    print(f"recovered shift: {result.shift} (chi-squared={result.chi_squared:.1f})")
    print(f"recovered plaintext: {result.plaintext}")
