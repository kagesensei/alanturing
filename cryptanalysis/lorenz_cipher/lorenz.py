"""Lorenz SZ40 cipher simulator: 5 chi wheels, 5 psi wheels, and the two
motor wheels that gate the psi wheels' irregular stepping.

Wheel lengths and the XOR keystream combination follow the historical
SZ40/42 design (source: Wikipedia's "Lorenz cipher" article). Stepping
follows the simpler SZ40-style "limitation": Mu61 steps every character;
Mu37 steps only when Mu61's current cam is set; the 5 psi wheels step
(together, as a group) only when Mu37's current cam is set. SZ42a's extra
"second chi wheel" limitation check is not modeled.

Plaintext characters use the ITA2 (Baudot-Murray) letters-shift 5-bit
code for A-Z and space; figures-shift and control characters are out of
scope. The pin patterns on every wheel are the "key" -- unlike Enigma's
fixed rotor wiring, there's no single historical pattern to hard-code, so
callers supply their own via `LorenzSettings`.
"""

from __future__ import annotations

from dataclasses import dataclass

CHI_LENGTHS = (41, 31, 29, 26, 23)
PSI_LENGTHS = (43, 47, 51, 53, 59)
MU61_LENGTH = 61
MU37_LENGTH = 37

ITA2_LETTERS: dict[str, str] = {
    "A": "00011", "B": "11001", "C": "01110", "D": "00010", "E": "00001",
    "F": "01101", "G": "11010", "H": "10101", "I": "00110", "J": "01011",
    "K": "01111", "L": "01001", "M": "11100", "N": "01100", "O": "11000",
    "P": "10110", "Q": "10111", "R": "01010", "S": "00101", "T": "10100",
    "U": "00111", "V": "11110", "W": "10011", "X": "11101", "Y": "10010",
    "Z": "10001", " ": "00100",
}
_ITA2_TO_CHAR: dict[str, str] = {code: char for char, code in ITA2_LETTERS.items()}


def text_to_bits(text: str) -> list[tuple[int, int, int, int, int]]:
    rows = []
    for char in text.upper():
        if char not in ITA2_LETTERS:
            raise ValueError(f"no ITA2 letters-shift code for {char!r}")
        rows.append(tuple(int(bit) for bit in ITA2_LETTERS[char]))
    return rows


def bits_to_text(rows) -> str:
    characters = []
    for row in rows:
        code = "".join(str(bit) for bit in row)
        if code not in _ITA2_TO_CHAR:
            raise ValueError(f"bit pattern {code!r} has no ITA2 letters-shift character")
        characters.append(_ITA2_TO_CHAR[code])
    return "".join(characters)


class Wheel:
    """One pin wheel: a fixed-length cycle of 0/1 cams and a position."""

    def __init__(self, length: int, pins: str, start_position: int = 0):
        if len(pins) != length or any(pin not in "01" for pin in pins):
            raise ValueError(f"pins must be a {length}-character string of 0s and 1s")
        if not 0 <= start_position < length:
            raise ValueError(f"start_position must be in [0, {length})")
        self.length = length
        self.pins = pins
        self.position = start_position

    def current_pin(self) -> bool:
        return self.pins[self.position] == "1"

    def step(self) -> None:
        self.position = (self.position + 1) % self.length


@dataclass
class LorenzSettings:
    """A full Lorenz key: every wheel's pin pattern and start position."""

    chi_pins: tuple[str, str, str, str, str]
    psi_pins: tuple[str, str, str, str, str]
    mu61_pins: str
    mu37_pins: str
    chi_start: tuple[int, int, int, int, int] = (0, 0, 0, 0, 0)
    psi_start: tuple[int, int, int, int, int] = (0, 0, 0, 0, 0)
    mu61_start: int = 0
    mu37_start: int = 0


class LorenzMachine:
    """SZ40-style Lorenz cipher. Symmetric like any Vernam/XOR stream
    cipher: the same call, with the same settings, both encrypts and
    decrypts (stepping never depends on the data being processed).
    """

    def __init__(self, settings: LorenzSettings):
        self.chi_wheels = [
            Wheel(length, pins, start)
            for length, pins, start in zip(CHI_LENGTHS, settings.chi_pins, settings.chi_start)
        ]
        self.psi_wheels = [
            Wheel(length, pins, start)
            for length, pins, start in zip(PSI_LENGTHS, settings.psi_pins, settings.psi_start)
        ]
        self.mu61 = Wheel(MU61_LENGTH, settings.mu61_pins, settings.mu61_start)
        self.mu37 = Wheel(MU37_LENGTH, settings.mu37_pins, settings.mu37_start)

    def _advance(self) -> None:
        mu37_will_step = self.mu61.current_pin()
        psi_will_step = self.mu37.current_pin()
        self.mu61.step()
        if mu37_will_step:
            self.mu37.step()
        if psi_will_step:
            for wheel in self.psi_wheels:
                wheel.step()
        for wheel in self.chi_wheels:
            wheel.step()

    def process_character(self, bits: tuple[int, ...]) -> tuple[int, ...]:
        """XOR `bits` with the current chi+psi keystream, then step."""
        chi_bits = (int(wheel.current_pin()) for wheel in self.chi_wheels)
        psi_bits = (int(wheel.current_pin()) for wheel in self.psi_wheels)
        keystream = (c ^ p for c, p in zip(chi_bits, psi_bits))
        output = tuple(b ^ k for b, k in zip(bits, keystream))
        self._advance()
        return output

    def process_text(self, text: str) -> list[tuple[int, ...]]:
        return [self.process_character(bits) for bits in text_to_bits(text)]

    def process_bits(self, rows) -> str:
        return bits_to_text([self.process_character(row) for row in rows])


if __name__ == "__main__":
    import random

    def _demo_pattern(length: int, seed: int) -> str:
        """A deterministic (not historically authentic) pin pattern for
        demo purposes -- real Lorenz pin patterns were a configurable
        daily key, not fixed hardware like Enigma's rotor wiring."""
        rng = random.Random(seed)
        return "".join(rng.choice("01") for _ in range(length))

    demo_settings = LorenzSettings(
        chi_pins=tuple(_demo_pattern(n, seed=100 + i) for i, n in enumerate(CHI_LENGTHS)),
        psi_pins=tuple(_demo_pattern(n, seed=200 + i) for i, n in enumerate(PSI_LENGTHS)),
        mu61_pins=_demo_pattern(MU61_LENGTH, seed=300),
        mu37_pins=_demo_pattern(MU37_LENGTH, seed=301),
    )

    message = "TURING AND TUTTE BOTH WORKED AT BLETCHLEY PARK"
    cipher_bits = LorenzMachine(demo_settings).process_text(message)
    print("ciphertext (bits):", " ".join("".join(map(str, row)) for row in cipher_bits))

    recovered = LorenzMachine(demo_settings).process_bits(cipher_bits)
    print("recovered:", recovered)
