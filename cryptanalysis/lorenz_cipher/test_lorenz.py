import unittest

from lorenz import (
    CHI_LENGTHS,
    MU37_LENGTH,
    MU61_LENGTH,
    PSI_LENGTHS,
    LorenzMachine,
    LorenzSettings,
    Wheel,
    bits_to_text,
    text_to_bits,
)


def pattern(length: int, one_every: int) -> str:
    """A simple deterministic pin pattern: 1 every `one_every` positions."""
    return "".join("1" if not i % one_every else "0" for i in range(length))


def settings_with(**overrides) -> LorenzSettings:
    defaults = {
        "chi_pins": tuple(pattern(n, 3) for n in CHI_LENGTHS),
        "psi_pins": tuple(pattern(n, 4) for n in PSI_LENGTHS),
        "mu61_pins": pattern(MU61_LENGTH, 2),
        "mu37_pins": pattern(MU37_LENGTH, 5),
    }
    defaults.update(overrides)
    return LorenzSettings(**defaults)


class TestTextBits(unittest.TestCase):
    def test_round_trips_letters_and_spaces(self):
        text = "HELLO WORLD"
        self.assertEqual(bits_to_text(text_to_bits(text)), text)

    def test_rejects_unsupported_character(self):
        with self.assertRaises(ValueError):
            text_to_bits("HELLO!")

    def test_bits_to_text_rejects_unmapped_code(self):
        with self.assertRaises(ValueError):
            bits_to_text([(1, 1, 1, 1, 1)])  # not a letters-shift code in the table


class TestWheel(unittest.TestCase):
    def test_rejects_wrong_length_pins(self):
        with self.assertRaises(ValueError):
            Wheel(5, "010")

    def test_rejects_non_binary_pins(self):
        with self.assertRaises(ValueError):
            Wheel(3, "012")

    def test_step_wraps_around(self):
        wheel = Wheel(3, "101", start_position=2)
        wheel.step()
        self.assertEqual(wheel.position, 0)


class TestLorenzMachine(unittest.TestCase):
    def test_decrypt_reverses_encrypt(self):
        settings = settings_with()
        plaintext = "THE QUICK BROWN FOX"

        cipher_bits = LorenzMachine(settings).process_text(plaintext)
        recovered = LorenzMachine(settings).process_bits(cipher_bits)

        self.assertEqual(recovered, plaintext)

    def test_ciphertext_differs_from_plaintext_bits(self):
        settings = settings_with()
        plaintext = "AAAAAAAAAA"
        cipher_bits = LorenzMachine(settings).process_text(plaintext)
        self.assertNotEqual(cipher_bits, text_to_bits(plaintext))

    def test_chi_wheels_step_every_character(self):
        settings = settings_with()
        machine = LorenzMachine(settings)
        starts = [wheel.position for wheel in machine.chi_wheels]

        machine.process_character((0, 0, 0, 0, 0))

        for wheel, start in zip(machine.chi_wheels, starts):
            self.assertEqual(wheel.position, (start + 1) % wheel.length)

    def test_psi_wheels_step_only_when_mu37_cam_is_set(self):
        # Force mu61's current cam on (so mu37 will step next) and mu37's
        # current cam on (so the psi wheels step *this* character).
        settings = settings_with(
            mu61_pins="1" + "0" * (MU61_LENGTH - 1),
            mu37_pins="1" + "0" * (MU37_LENGTH - 1),
        )
        machine = LorenzMachine(settings)
        psi_starts = [wheel.position for wheel in machine.psi_wheels]

        machine.process_character((0, 0, 0, 0, 0))

        for wheel, start in zip(machine.psi_wheels, psi_starts):
            self.assertEqual(wheel.position, (start + 1) % wheel.length)

        # On the next character, mu37's cam (now at index 1, which is 0)
        # is clear, so the psi wheels must NOT step this time.
        psi_after_first = [wheel.position for wheel in machine.psi_wheels]
        machine.process_character((0, 0, 0, 0, 0))
        for wheel, before in zip(machine.psi_wheels, psi_after_first):
            self.assertEqual(wheel.position, before)


if __name__ == "__main__":
    unittest.main(verbosity=2)
