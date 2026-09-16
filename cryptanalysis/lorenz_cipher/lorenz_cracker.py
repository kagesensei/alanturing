"""Known-plaintext recovery of the 5 chi-wheel pin patterns.

Scope: wheel START POSITIONS, the psi wheels' pin patterns, and the two
motor wheels' pin patterns and start positions are all assumed already
known -- only the chi wheels' patterns are recovered here. This mirrors
the real, two-stage historical process (Bletchley Park first found wheel
*start positions* per message via statistical search -- the famous "1+2
break-in" -- then derived/confirmed pin *patterns* from enough depth of
known traffic); this module models the second stage only, and does it
exactly rather than statistically, since a known plaintext-ciphertext
pair is much stronger than the ciphertext-only depth Bletchley worked
from.

Because chi wheels step every character unconditionally (unlike the
irregularly-stepping psi wheels), the psi/motor contribution at every
character position can be computed independently of the (unknown) chi
wheels, then subtracted out of the known keystream (plaintext XOR
ciphertext) exactly. What's left is each chi wheel's own contribution --
and since a chi wheel repeats every `length` characters, enough known
plaintext to cover one full period pins its entire pattern down
deterministically, with no statistics or guessing involved.
"""

from __future__ import annotations

from dataclasses import dataclass

from lorenz import CHI_LENGTHS, MU37_LENGTH, MU61_LENGTH, PSI_LENGTHS, Wheel, text_to_bits


@dataclass
class KnownPsiMotor:
    """Everything about a Lorenz key except the unknown chi wheel
    patterns -- what `recover_chi_patterns` needs already known."""

    psi_pins: tuple[str, str, str, str, str]
    mu61_pins: str
    mu37_pins: str
    chi_start: tuple[int, int, int, int, int] = (0, 0, 0, 0, 0)
    psi_start: tuple[int, int, int, int, int] = (0, 0, 0, 0, 0)
    mu61_start: int = 0
    mu37_start: int = 0


def _psi_motor_contribution(known: KnownPsiMotor, num_characters: int) -> list[tuple[int, ...]]:
    """The psi wheels' contribution to the keystream at each of the first
    `num_characters` positions -- entirely independent of the chi wheels.
    """
    psi_wheels = [
        Wheel(length, pins, start)
        for length, pins, start in zip(PSI_LENGTHS, known.psi_pins, known.psi_start)
    ]
    mu61 = Wheel(MU61_LENGTH, known.mu61_pins, known.mu61_start)
    mu37 = Wheel(MU37_LENGTH, known.mu37_pins, known.mu37_start)

    contributions = []
    for _ in range(num_characters):
        contributions.append(tuple(int(wheel.current_pin()) for wheel in psi_wheels))
        mu37_will_step = mu61.current_pin()
        psi_will_step = mu37.current_pin()
        mu61.step()
        if mu37_will_step:
            mu37.step()
        if psi_will_step:
            for wheel in psi_wheels:
                wheel.step()
    return contributions


def _recover_one_wheel(
    wheel_index: int, length: int, start: int, plaintext_bits, ciphertext_bits, psi_contribution
) -> str:
    pins: list[int | None] = [None] * length
    for position, (plain_row, cipher_row, psi_row) in enumerate(
        zip(plaintext_bits, ciphertext_bits, psi_contribution)
    ):
        keystream_bit = plain_row[wheel_index] ^ cipher_row[wheel_index]
        chi_bit = keystream_bit ^ psi_row[wheel_index]
        pin_index = (start + position) % length
        if pins[pin_index] is None:
            pins[pin_index] = chi_bit
        elif pins[pin_index] != chi_bit:
            raise ValueError(
                f"inconsistent chi wheel {wheel_index + 1} pin at index {pin_index}; "
                "check that `known` matches the settings actually used"
            )
    return "".join(str(bit) for bit in pins)


def recover_chi_patterns(
    plaintext: str, ciphertext_bits: list[tuple[int, ...]], known: KnownPsiMotor
) -> tuple[str, str, str, str, str]:
    """Recover the 5 chi wheels' pin patterns from a known plaintext and
    its ciphertext (as produced by `LorenzMachine.process_text`).
    """
    longest_period = max(CHI_LENGTHS)
    if len(plaintext) < longest_period:
        raise ValueError(
            f"need at least {longest_period} characters of known plaintext "
            "to cover every chi wheel's full period"
        )
    plaintext_bits = text_to_bits(plaintext)
    if len(plaintext_bits) != len(ciphertext_bits):
        raise ValueError("plaintext and ciphertext must have the same length")

    psi_contribution = _psi_motor_contribution(known, len(plaintext_bits))
    return tuple(
        _recover_one_wheel(
            wheel_index, length, known.chi_start[wheel_index],
            plaintext_bits, ciphertext_bits, psi_contribution,
        )
        for wheel_index, length in enumerate(CHI_LENGTHS)
    )


if __name__ == "__main__":
    import random

    from lorenz import LorenzMachine, LorenzSettings

    def _demo_pattern(length: int, seed: int) -> str:
        rng = random.Random(seed)
        return "".join(rng.choice("01") for _ in range(length))

    secret_chi_pins = tuple(_demo_pattern(n, seed=100 + i) for i, n in enumerate(CHI_LENGTHS))
    secret_settings = LorenzSettings(
        chi_pins=secret_chi_pins,
        psi_pins=tuple(_demo_pattern(n, seed=200 + i) for i, n in enumerate(PSI_LENGTHS)),
        mu61_pins=_demo_pattern(MU61_LENGTH, seed=300),
        mu37_pins=_demo_pattern(MU37_LENGTH, seed=301),
    )

    long_message = (
        "THE LORENZ CIPHER WAS FAR MORE COMPLEX THAN ENIGMA AND ITS BREAK BY "
        "BILL TUTTE WITHOUT EVER SEEING THE MACHINE ITSELF REMAINS ONE OF THE "
        "GREATEST FEATS OF WORLD WAR TWO CRYPTANALYSIS AND LED DIRECTLY TO "
        "COLOSSUS THE WORLDS FIRST PROGRAMMABLE ELECTRONIC COMPUTER"
    )
    intercepted_bits = LorenzMachine(secret_settings).process_text(long_message)

    known_psi_motor = KnownPsiMotor(
        psi_pins=secret_settings.psi_pins,
        mu61_pins=secret_settings.mu61_pins,
        mu37_pins=secret_settings.mu37_pins,
    )
    recovered_chi_pins = recover_chi_patterns(long_message, intercepted_bits, known_psi_motor)

    print("recovered == actual:", recovered_chi_pins == secret_chi_pins)
    for i, (actual, recovered) in enumerate(zip(secret_chi_pins, recovered_chi_pins), start=1):
        print(f"  chi{i}: {actual} -> {recovered}")
