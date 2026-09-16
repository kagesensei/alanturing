"""Automated Enigma key discovery: given a known plaintext-ciphertext
message pair (e.g. an intercept whose content was later confirmed --
historically, often because it was a predictable weather report or
routine sign-off), automatically recovers the full key.

This applies the Bombe's menu-consistency technique (see bombe_simulator)
twice: first cheaply, against a short crib, to find the correct rotor
order and start position out of the whole search space; then once more,
against the *entire* known plaintext, to resolve as much of the plugboard
as that much data supports. The result is verified by an exact
decrypt-and-compare against the full known plaintext, so a "discovered"
key is never just a plausible guess.

Ring settings are assumed known, matching brute_force_cracker/bombe's
scope -- this module discovers rotor order, start position, and plugboard.
"""

from __future__ import annotations

import itertools
import sys
from dataclasses import dataclass
from pathlib import Path

_ENIGMA_SIMULATOR_DIR = Path(__file__).resolve().parent.parent / "enigma_simulator"
_BOMBE_SIMULATOR_DIR = Path(__file__).resolve().parent.parent / "bombe_simulator"
for _directory in (_ENIGMA_SIMULATOR_DIR, _BOMBE_SIMULATOR_DIR):
    if str(_directory) not in sys.path:
        sys.path.insert(0, str(_directory))

from enigma import ALPHABET, EnigmaMachine, EnigmaSettings  # pylint: disable=wrong-import-position
from bombe import (  # pylint: disable=wrong-import-position
    _build_menu_edges,
    _unsteckered_permutations,
    find_bombe_stops,
    find_consistent_plugboard,
)


@dataclass
class DiscoveredKey:
    rotor_names: tuple[str, str, str]
    start_positions: tuple[str, str, str]
    plugboard_pairs: tuple[tuple[str, str], ...]
    fully_verified: bool


def _only_letters(text: str) -> str:
    return "".join(char for char in text.upper() if char in ALPHABET)


def _resolve_full_plugboard(
    plaintext: str,
    ciphertext: str,
    rotor_names: tuple[str, str, str],
    start_positions: tuple[str, str, str],
    ring_settings: tuple[str, str, str],
    reflector_name: str,
) -> dict[str, str] | None:
    permutations = _unsteckered_permutations(
        rotor_names, ring_settings, start_positions, reflector_name, len(plaintext)
    )
    edges = _build_menu_edges(plaintext, ciphertext, permutations)
    return find_consistent_plugboard(edges)


def _canonical_pairs(plugboard: dict[str, str]) -> tuple[tuple[str, str], ...]:
    pairs = {tuple(sorted((a, b))) for a, b in plugboard.items() if a != b}
    return tuple(sorted(pairs))


def _verify_and_build_result(
    plaintext_letters: str,
    cipher_letters: str,
    rotor_names: tuple[str, str, str],
    start_positions: tuple[str, str, str],
    ring_settings: tuple[str, str, str],
    reflector_name: str,
    plugboard: dict[str, str],
) -> DiscoveredKey:
    pairs = _canonical_pairs(plugboard)
    settings = EnigmaSettings(
        rotor_names=rotor_names,
        ring_settings=ring_settings,
        start_positions=start_positions,
        reflector_name=reflector_name,
        plugboard_pairs=pairs,
    )
    decrypted = EnigmaMachine(settings).encrypt_message(cipher_letters)
    return DiscoveredKey(rotor_names, start_positions, pairs, decrypted == plaintext_letters)


def _unique_setting(stops) -> tuple[tuple[str, str, str], tuple[str, str, str]]:
    """The single (rotor_names, start_positions) pair every stop agrees
    on, or a ValueError if the crib left more than one candidate.
    """
    settings = {(stop.rotor_names, stop.start_positions) for stop in stops}
    if len(settings) > 1:
        raise ValueError(
            f"{len(settings)} candidate settings remain consistent; "
            "try a longer crib_length or more known plaintext to disambiguate"
        )
    return next(iter(settings))


def discover_key(
    plaintext: str,
    ciphertext: str,
    *,
    crib_length: int = 16,
    available_rotors: tuple[str, ...] = ("I", "II", "III", "IV", "V"),
    reflector_name: str = "B",
    ring_settings: tuple[str, str, str] = ("A", "A", "A"),
    start_position_candidates: list[tuple[str, str, str]] | None = None,
) -> DiscoveredKey:
    """Recover the rotor order, start position, and plugboard that turn
    `plaintext` into `ciphertext` (ring settings assumed already known).
    """
    plaintext_letters = _only_letters(plaintext)
    cipher_letters = _only_letters(ciphertext)
    if len(plaintext_letters) != len(cipher_letters):
        raise ValueError("plaintext and ciphertext must have the same number of A-Z letters")
    if len(plaintext_letters) < crib_length:
        raise ValueError(f"need at least {crib_length} letters of known plaintext")

    stops = find_bombe_stops(
        cipher_letters,
        plaintext_letters[:crib_length],
        available_rotors=available_rotors,
        reflector_name=reflector_name,
        ring_settings=ring_settings,
        start_position_candidates=start_position_candidates,
    )
    if not stops:
        raise ValueError("no consistent rotor order/start position found for this crib")
    rotor_names, start_positions = _unique_setting(stops)

    full_plugboard = _resolve_full_plugboard(
        plaintext_letters,
        cipher_letters,
        rotor_names,
        start_positions,
        ring_settings,
        reflector_name,
    )
    if full_plugboard is None:
        raise ValueError(
            "the candidate found from the short crib was contradicted by the "
            "rest of the known plaintext -- it was a false stop"
        )
    return _verify_and_build_result(
        plaintext_letters,
        cipher_letters,
        rotor_names,
        start_positions,
        ring_settings,
        reflector_name,
        full_plugboard,
    )


if __name__ == "__main__":
    secret_settings = EnigmaSettings(
        rotor_names=("III", "V", "I"),
        start_positions=("Q", "E", "L"),
        plugboard_pairs=(("B", "Z"), ("H", "Y"), ("K", "P"), ("Q", "X")),
    )
    known_plaintext = (
        "WEATHERREPORTFORMORNINGWATCHTWELVETHOUSANDMETERSCLEARSKIESLIGHTWIND"
    )
    known_ciphertext = EnigmaMachine(secret_settings).encrypt_message(known_plaintext)
    print(f"ciphertext: {known_ciphertext}")

    # An exhaustive search (6 rotor orders x 17,576 positions, the
    # minimum with only 3 rotors available) takes well over a minute in
    # pure Python. This demo samples the position space instead (always
    # including the true one) so it runs in a few seconds -- pass
    # start_position_candidates=None (the default) for an exhaustive run.
    all_positions = list(itertools.product(ALPHABET, repeat=3))
    sample_positions = all_positions[::200]
    if secret_settings.start_positions not in sample_positions:
        sample_positions.append(secret_settings.start_positions)

    discovered = discover_key(
        known_plaintext,
        known_ciphertext,
        available_rotors=("I", "III", "V"),
        start_position_candidates=sample_positions,
    )
    print(f"rotors={discovered.rotor_names} start={discovered.start_positions}")
    print(f"plugboard_pairs={discovered.plugboard_pairs}")
    print(f"fully_verified={discovered.fully_verified}")
