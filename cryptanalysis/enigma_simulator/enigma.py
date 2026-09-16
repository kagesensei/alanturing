"""Enigma I simulator: rotors, reflector, plugboard, and rotor stepping.

Historical wiring for rotors I-V and reflectors A-C, matching the
Wehrmacht/Luftwaffe Enigma I. Source: Wikipedia's "Enigma rotor details"
and codesandciphers.org.uk's rotor specification tables.
"""

from __future__ import annotations

from dataclasses import dataclass, field

ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
ALPHABET_SIZE = len(ALPHABET)

ROTOR_WIRINGS: dict[str, str] = {
    "I": "EKMFLGDQVZNTOWYHXUSPAIBRCJ",
    "II": "AJDKSIRUXBLHWTMCQGZNPYFVOE",
    "III": "BDFHJLCPRTXVZNYEIWGAKMUSQO",
    "IV": "ESOVPZJAYQUIRHXLNFTGKDCMWB",
    "V": "VZBRGITYUPSDNHLXAWMJQOFECK",
}

ROTOR_NOTCHES: dict[str, str] = {
    "I": "Q",
    "II": "E",
    "III": "V",
    "IV": "J",
    "V": "Z",
}

REFLECTOR_WIRINGS: dict[str, str] = {
    "A": "EJMZALYXVBWFCRQUONTSPIKHGD",
    "B": "YRUHQSLDPXNGOKMIEBFZCWVJAT",
    "C": "FVPJIAOYEDRZXWGCTKUQSBNMHL",
}


def _validate_letter(label: str, letter: str) -> None:
    if letter not in ALPHABET:
        raise ValueError(f"{label} must be a single A-Z letter, got {letter!r}")


class Rotor:
    """One Enigma rotor: fixed wiring, a ring setting, and a live position."""

    def __init__(self, name: str, ring_setting: str = "A", start_position: str = "A"):
        if name not in ROTOR_WIRINGS:
            raise ValueError(f"unknown rotor {name!r}; choose from {sorted(ROTOR_WIRINGS)}")
        _validate_letter("ring_setting", ring_setting)
        _validate_letter("start_position", start_position)
        self.name = name
        self.wiring = ROTOR_WIRINGS[name]
        self.notch = ROTOR_NOTCHES[name]
        self.ring_offset = ALPHABET.index(ring_setting)
        self.position = ALPHABET.index(start_position)

    def at_notch(self) -> bool:
        """True if this rotor is positioned to trigger the next rotor's step."""
        return ALPHABET[self.position] == self.notch

    def step(self) -> None:
        self.position = (self.position + 1) % ALPHABET_SIZE

    def forward(self, index: int) -> int:
        """Signal path from the entry side toward the reflector."""
        shift = self.position - self.ring_offset
        entry = (index + shift) % ALPHABET_SIZE
        wired = ALPHABET.index(self.wiring[entry])
        return (wired - shift) % ALPHABET_SIZE

    def backward(self, index: int) -> int:
        """Signal path from the reflector back toward the entry side."""
        shift = self.position - self.ring_offset
        entry = (index + shift) % ALPHABET_SIZE
        wired = self.wiring.index(ALPHABET[entry])
        return (wired - shift) % ALPHABET_SIZE


class Reflector:
    """Fixed wiring that turns the signal back through the rotors."""

    def __init__(self, name: str = "B"):
        if name not in REFLECTOR_WIRINGS:
            raise ValueError(
                f"unknown reflector {name!r}; choose from {sorted(REFLECTOR_WIRINGS)}"
            )
        self.name = name
        self.wiring = REFLECTOR_WIRINGS[name]

    def reflect(self, index: int) -> int:
        return ALPHABET.index(self.wiring[index])


class Plugboard:
    """Swaps pairs of letters before entry and after the return path."""

    def __init__(self, pairs: tuple[tuple[str, str], ...] = ()):
        mapping = {letter: letter for letter in ALPHABET}
        used: set[str] = set()
        for first, second in pairs:
            _validate_letter("plugboard letter", first)
            _validate_letter("plugboard letter", second)
            if first == second:
                raise ValueError(f"plugboard cannot pair a letter with itself: {first!r}")
            if first in used or second in used:
                raise ValueError(f"letter used in more than one plugboard pair: {first!r}")
            mapping[first], mapping[second] = second, first
            used.add(first)
            used.add(second)
        self.mapping = mapping

    def swap(self, letter: str) -> str:
        return self.mapping[letter]


@dataclass
class EnigmaSettings:
    """A full Enigma I configuration: rotors given left to right."""

    rotor_names: tuple[str, str, str]
    ring_settings: tuple[str, str, str] = ("A", "A", "A")
    start_positions: tuple[str, str, str] = ("A", "A", "A")
    reflector_name: str = "B"
    plugboard_pairs: tuple[tuple[str, str], ...] = field(default_factory=tuple)


class EnigmaMachine:
    """A 3-rotor Enigma I. `encrypt_letter`/`encrypt_message` are symmetric:
    running the same settings over ciphertext recovers the plaintext.
    """

    def __init__(self, settings: EnigmaSettings):
        if len(settings.rotor_names) != 3:
            raise ValueError("exactly three rotors are required (left, middle, right)")
        self.rotors = [
            Rotor(name, ring, start)
            for name, ring, start in zip(
                settings.rotor_names, settings.ring_settings, settings.start_positions
            )
        ]
        self.reflector = Reflector(settings.reflector_name)
        self.plugboard = Plugboard(settings.plugboard_pairs)

    def _step_rotors(self) -> None:
        left, middle, right = self.rotors
        middle_will_step = middle.at_notch()
        right_will_step = right.at_notch()
        if middle_will_step:
            left.step()
            middle.step()
        elif right_will_step:
            middle.step()
        right.step()

    def step(self) -> None:
        """Advance the rotors exactly as a real keypress would, without
        substituting a letter. Pairs with `substitute()` for callers (e.g.
        the Bombe simulator) that need the rotor state at each position
        independently of processing a signal through it.
        """
        self._step_rotors()

    def substitute(self, letter: str) -> str:
        """Run `letter` through the plugboard/rotors/reflector at the
        *current* rotor position, without stepping first.
        """
        _validate_letter("letter", letter)
        index = ALPHABET.index(self.plugboard.swap(letter))
        for rotor in reversed(self.rotors):
            index = rotor.forward(index)
        index = self.reflector.reflect(index)
        for rotor in self.rotors:
            index = rotor.backward(index)
        return self.plugboard.swap(ALPHABET[index])

    def encrypt_letter(self, letter: str) -> str:
        self.step()
        return self.substitute(letter)

    def encrypt_message(self, text: str) -> str:
        """Encrypt `text`, dropping anything that isn't an A-Z letter."""
        letters = (char for char in text.upper() if char in ALPHABET)
        return "".join(self.encrypt_letter(letter) for letter in letters)


if __name__ == "__main__":
    wehrmacht_settings = EnigmaSettings(
        rotor_names=("I", "II", "III"),
        plugboard_pairs=(("A", "B"), ("C", "D")),
    )

    machine = EnigmaMachine(wehrmacht_settings)
    plaintext = "ENIGMAWASBROKENBYTURING"
    ciphertext = machine.encrypt_message(plaintext)
    print(f"{plaintext} -> {ciphertext}")

    decoder = EnigmaMachine(wehrmacht_settings)
    recovered = decoder.encrypt_message(ciphertext)
    print(f"{ciphertext} -> {recovered}")
