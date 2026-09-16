"""Brute-force Enigma cracker: try every rotor order and start position,
looking for one whose decryption begins with a known plaintext crib.

Ring settings and the plugboard are assumed already known (cracking those
too by brute force alone is computationally infeasible -- that's what the
later Bombe simulation and automated key discovery are for). This mirrors
the historical pre-Bombe approach: with only rotor order and position
unknown, the search space is small enough to try exhaustively.
"""

from __future__ import annotations

import itertools
import sys
from dataclasses import dataclass
from pathlib import Path

# Reuses the tested Enigma engine from the sibling roadmap item instead of
# re-implementing rotor/reflector/plugboard logic a second time.
_ENIGMA_SIMULATOR_DIR = Path(__file__).resolve().parent.parent / "enigma_simulator"
if str(_ENIGMA_SIMULATOR_DIR) not in sys.path:
    sys.path.insert(0, str(_ENIGMA_SIMULATOR_DIR))

from enigma import ALPHABET, EnigmaMachine, EnigmaSettings  # pylint: disable=wrong-import-position


@dataclass
class CrackResult:
    """One rotor order/start position combination whose decryption
    begins with the requested crib."""

    rotor_names: tuple[str, str, str]
    start_positions: tuple[str, str, str]
    decrypted: str


def _decryption_matches_crib(settings: EnigmaSettings, letters: list[str], crib: str) -> bool:
    machine = EnigmaMachine(settings)
    for cipher_letter, crib_letter in zip(letters, crib):
        if machine.encrypt_letter(cipher_letter) != crib_letter:
            return False
    return True


def crack(
    ciphertext: str,
    crib: str,
    available_rotors: tuple[str, ...] = ("I", "II", "III", "IV", "V"),
    reflector_name: str = "B",
    ring_settings: tuple[str, str, str] = ("A", "A", "A"),
    plugboard_pairs: tuple[tuple[str, str], ...] = (),
) -> list[CrackResult]:
    """Search every (rotor order, start position) pair for one that decrypts
    `ciphertext` to something starting with `crib`. Returns every match
    found (usually one, occasionally a rare false positive on short cribs).
    """
    letters = [char for char in ciphertext.upper() if char in ALPHABET]
    crib = crib.upper()
    if not crib or any(char not in ALPHABET for char in crib):
        raise ValueError("crib must be a non-empty string of A-Z letters")
    if len(crib) > len(letters):
        raise ValueError("crib cannot be longer than the ciphertext")

    matches: list[CrackResult] = []
    for rotor_names in itertools.permutations(available_rotors, 3):
        for start_positions in itertools.product(ALPHABET, repeat=3):
            settings = EnigmaSettings(
                rotor_names=rotor_names,
                ring_settings=ring_settings,
                start_positions=start_positions,
                reflector_name=reflector_name,
                plugboard_pairs=plugboard_pairs,
            )
            if not _decryption_matches_crib(settings, letters, crib):
                continue
            full_decryption = EnigmaMachine(settings).encrypt_message("".join(letters))
            matches.append(CrackResult(rotor_names, start_positions, full_decryption))
    return matches


if __name__ == "__main__":
    secret_settings = EnigmaSettings(
        rotor_names=("III", "I", "IV"), start_positions=("Q", "E", "V")
    )
    secret_plaintext = "THEBOMBEWILLFINDTHISKEY"
    secret_ciphertext = EnigmaMachine(secret_settings).encrypt_message(secret_plaintext)
    print(f"ciphertext: {secret_ciphertext}")

    found = crack(secret_ciphertext, crib="THEBOMBE")
    for result in found:
        print(
            f"rotors={result.rotor_names} start={result.start_positions} "
            f"-> {result.decrypted}"
        )
