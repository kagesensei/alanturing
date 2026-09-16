"""Simplified simulation of Turing's Bombe: the key insight it automated
was that the Enigma plugboard never needs to be brute forced at all. For
a candidate rotor order and start position, a "menu" built from a crib
(a known plaintext fragment aligned with ciphertext) can be checked for
*consistency* -- do the crib's repeated letters force a contradiction? --
without ever guessing a plugboard wiring. A setting with no contradiction
is a "stop": a candidate worth testing further (historically, by hand at
Bletchley Park; here, its deduced partial plugboard is returned too).

Ring settings are assumed known, matching brute_force_cracker's scope.
The deduced plugboard only covers letters actually connected to the crib's
"menu" graph -- a short or non-repeating crib resolves little, exactly as
with the real machine, which is why cribs were chosen for their loops.
"""

from __future__ import annotations

import itertools
import sys
from dataclasses import dataclass
from pathlib import Path

_ENIGMA_SIMULATOR_DIR = Path(__file__).resolve().parent.parent / "enigma_simulator"
if str(_ENIGMA_SIMULATOR_DIR) not in sys.path:
    sys.path.insert(0, str(_ENIGMA_SIMULATOR_DIR))

from enigma import ALPHABET, EnigmaMachine, EnigmaSettings  # pylint: disable=wrong-import-position

_MAX_PLUGBOARD_ROUNDS = len(ALPHABET)


@dataclass
class BombeStop:
    """A rotor order/start position that survived consistency checking,
    with the (possibly partial) plugboard wiring the crib's menu implied.
    """

    rotor_names: tuple[str, str, str]
    start_positions: tuple[str, str, str]
    plugboard: dict[str, str]


def _unsteckered_permutations(
    rotor_names: tuple[str, str, str],
    ring_settings: tuple[str, str, str],
    start_positions: tuple[str, str, str],
    reflector_name: str,
    length: int,
) -> list[dict[str, str]]:
    """The rotor+reflector permutation at each of `length` key positions,
    with an empty (identity) plugboard -- what the machine does to a
    signal before any plugboard wiring is considered.
    """
    settings = EnigmaSettings(
        rotor_names=rotor_names,
        ring_settings=ring_settings,
        start_positions=start_positions,
        reflector_name=reflector_name,
    )
    machine = EnigmaMachine(settings)
    permutations = []
    for _ in range(length):
        machine.step()
        permutations.append({letter: machine.substitute(letter) for letter in ALPHABET})
    return permutations


def _build_menu_edges(crib: str, cipher_segment: str, permutations: list[dict[str, str]]):
    return [
        (crib_letter, cipher_letter, permutation, {v: k for k, v in permutation.items()})
        for crib_letter, cipher_letter, permutation in zip(crib, cipher_segment, permutations)
    ]


def _solve_plugboard(edges, trial_letter: str, trial_partner: str) -> dict[str, str] | None:
    """Hypothesize that the plugboard wires `trial_letter` to
    `trial_partner`, then propagate that through the menu's edges until
    nothing new is learned. Returns the resulting plugboard, or None the
    moment a contradiction (a letter forced to two different partners) is
    found.
    """
    plugboard: dict[str, str] = {}

    def assign(letter: str, partner: str) -> bool:
        if letter in plugboard:
            return plugboard[letter] == partner
        if partner in plugboard:
            return plugboard[partner] == letter
        plugboard[letter] = partner
        plugboard[partner] = letter
        return True

    if not assign(trial_letter, trial_partner):
        return None

    for _ in range(_MAX_PLUGBOARD_ROUNDS):
        changed = False
        for crib_letter, cipher_letter, permutation, inverse in edges:
            before = len(plugboard)
            if crib_letter in plugboard:
                if not assign(cipher_letter, permutation[plugboard[crib_letter]]):
                    return None
            if cipher_letter in plugboard:
                if not assign(crib_letter, inverse[plugboard[cipher_letter]]):
                    return None
            changed = changed or len(plugboard) != before
        if not changed:
            break
    return plugboard


def find_consistent_plugboard(edges) -> dict[str, str] | None:
    """Try every possible partner (including "unplugged") for the first
    crib letter in `edges`, returning the first hypothesis that
    propagates through the whole menu without contradiction.
    """
    trial_letter = edges[0][0]
    for trial_partner in ALPHABET:
        plugboard = _solve_plugboard(edges, trial_letter, trial_partner)
        if plugboard is not None:
            return plugboard
    return None


def find_bombe_stops(
    ciphertext: str,
    crib: str,
    available_rotors: tuple[str, ...] = ("I", "II", "III", "IV", "V"),
    reflector_name: str = "B",
    ring_settings: tuple[str, str, str] = ("A", "A", "A"),
    start_position_candidates: list[tuple[str, str, str]] | None = None,
) -> list[BombeStop]:
    """Search every rotor order, and every start position in
    `start_position_candidates` (all 17,576 by default -- pass a smaller
    list to restrict the search, e.g. to positions already narrowed down
    some other way), for "stops": settings where the crib's menu is
    internally consistent for at least one plugboard hypothesis. Wrong
    settings are rejected without brute forcing the plugboard -- the
    Bombe's key trick.
    """
    letters = [char for char in ciphertext.upper() if char in ALPHABET]
    crib = crib.upper()
    if not crib or any(char not in ALPHABET for char in crib):
        raise ValueError("crib must be a non-empty string of A-Z letters")
    if len(crib) > len(letters):
        raise ValueError("crib cannot be longer than the ciphertext")
    if start_position_candidates is None:
        start_position_candidates = list(itertools.product(ALPHABET, repeat=3))

    cipher_segment = "".join(letters[: len(crib)])
    stops: list[BombeStop] = []
    for rotor_names in itertools.permutations(available_rotors, 3):
        for start_positions in start_position_candidates:
            permutations = _unsteckered_permutations(
                rotor_names, ring_settings, start_positions, reflector_name, len(crib)
            )
            edges = _build_menu_edges(crib, cipher_segment, permutations)
            plugboard = find_consistent_plugboard(edges)
            if plugboard is not None:
                stops.append(BombeStop(rotor_names, start_positions, plugboard))
    return stops


if __name__ == "__main__":
    secret_settings = EnigmaSettings(
        rotor_names=("II", "I", "III"),
        start_positions=("B", "R", "U"),
        plugboard_pairs=(("A", "M"), ("F", "I"), ("N", "V")),
    )
    secret_plaintext = "ATTACKATDAWNNEARTHEBRIDGEATTACKATDAWN"
    secret_ciphertext = EnigmaMachine(secret_settings).encrypt_message(secret_plaintext)
    print(f"ciphertext: {secret_ciphertext}")

    # An exhaustive search (6 rotor orders x 17,576 positions, the
    # minimum with only 3 rotors available) takes about 90 seconds in
    # pure Python. This demo samples the position space instead (always
    # including the true one) so it runs in a couple of seconds -- pass
    # start_position_candidates=None (the default) for an exhaustive run.
    all_positions = list(itertools.product(ALPHABET, repeat=3))
    sample_positions = all_positions[::200]
    if secret_settings.start_positions not in sample_positions:
        sample_positions.append(secret_settings.start_positions)

    found_stops = find_bombe_stops(
        secret_ciphertext,
        crib="ATTACKATDAWN",
        available_rotors=("I", "II", "III"),
        start_position_candidates=sample_positions,
    )
    print(f"{len(found_stops)} stop(s) out of {6 * len(sample_positions)} sampled candidates:")
    for stop in found_stops:
        print(f"  rotors={stop.rotor_names} start={stop.start_positions}")
        print(f"    plugboard={stop.plugboard}")
