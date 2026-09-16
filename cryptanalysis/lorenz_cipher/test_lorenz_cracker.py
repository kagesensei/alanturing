import unittest

from lorenz import PSI_LENGTHS, LorenzMachine
from lorenz_cracker import KnownPsiMotor, recover_chi_patterns
from test_lorenz import pattern, settings_with as _secret_settings

LONG_MESSAGE = (
    "THE LORENZ CIPHER WAS FAR MORE COMPLEX THAN ENIGMA AND ITS BREAK BY "
    "BILL TUTTE WITHOUT EVER SEEING THE MACHINE ITSELF REMAINS ONE OF THE "
    "GREATEST FEATS OF WORLD WAR TWO CRYPTANALYSIS AND LED DIRECTLY TO "
    "COLOSSUS THE WORLDS FIRST PROGRAMMABLE ELECTRONIC COMPUTER"
)


class TestRecoverChiPatterns(unittest.TestCase):
    def test_recovers_exact_patterns_from_a_long_known_message(self):
        settings = _secret_settings()
        ciphertext_bits = LorenzMachine(settings).process_text(LONG_MESSAGE)

        known = KnownPsiMotor(
            psi_pins=settings.psi_pins, mu61_pins=settings.mu61_pins, mu37_pins=settings.mu37_pins
        )
        recovered = recover_chi_patterns(LONG_MESSAGE, ciphertext_bits, known)

        self.assertEqual(recovered, settings.chi_pins)

    def test_recovers_exact_patterns_with_nonzero_start_positions(self):
        settings = _secret_settings(
            chi_start=(5, 10, 2, 20, 7), psi_start=(1, 2, 3, 4, 5), mu61_start=6, mu37_start=8
        )
        ciphertext_bits = LorenzMachine(settings).process_text(LONG_MESSAGE)

        known = KnownPsiMotor(
            psi_pins=settings.psi_pins,
            mu61_pins=settings.mu61_pins,
            mu37_pins=settings.mu37_pins,
            chi_start=settings.chi_start,
            psi_start=settings.psi_start,
            mu61_start=settings.mu61_start,
            mu37_start=settings.mu37_start,
        )
        recovered = recover_chi_patterns(LONG_MESSAGE, ciphertext_bits, known)

        self.assertEqual(recovered, settings.chi_pins)

    def test_rejects_plaintext_shorter_than_longest_chi_period(self):
        settings = _secret_settings()
        short_message = "TOO SHORT"
        ciphertext_bits = LorenzMachine(settings).process_text(short_message)
        known = KnownPsiMotor(
            psi_pins=settings.psi_pins, mu61_pins=settings.mu61_pins, mu37_pins=settings.mu37_pins
        )

        with self.assertRaises(ValueError):
            recover_chi_patterns(short_message, ciphertext_bits, known)

    def test_wrong_known_psi_motor_raises_inconsistency_error(self):
        settings = _secret_settings()
        ciphertext_bits = LorenzMachine(settings).process_text(LONG_MESSAGE)

        wrong_known = KnownPsiMotor(
            psi_pins=tuple(pattern(n, 7) for n in PSI_LENGTHS),  # doesn't match settings
            mu61_pins=settings.mu61_pins,
            mu37_pins=settings.mu37_pins,
        )

        with self.assertRaises(ValueError):
            recover_chi_patterns(LONG_MESSAGE, ciphertext_bits, wrong_known)


if __name__ == "__main__":
    unittest.main(verbosity=2)
