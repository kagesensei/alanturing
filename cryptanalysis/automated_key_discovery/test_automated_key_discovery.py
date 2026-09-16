import itertools
import unittest

from automated_key_discovery import ALPHABET, discover_key
from enigma import EnigmaMachine, EnigmaSettings

SECRET_SETTINGS = EnigmaSettings(
    rotor_names=("III", "V", "I"),
    start_positions=("Q", "E", "L"),
    plugboard_pairs=(("B", "Z"), ("H", "Y"), ("K", "P"), ("Q", "X")),
)
KNOWN_PLAINTEXT = "WEATHERREPORTFORMORNINGWATCHTWELVETHOUSANDMETERSCLEARSKIESLIGHTWIND"


def _sample_positions(step, include):
    positions = list(itertools.product(ALPHABET, repeat=3))[::step]
    for extra in include:
        if extra not in positions:
            positions.append(extra)
    return positions


class TestDiscoverKey(unittest.TestCase):
    def test_recovers_full_key_from_known_plaintext(self):
        ciphertext = EnigmaMachine(SECRET_SETTINGS).encrypt_message(KNOWN_PLAINTEXT)
        candidates = _sample_positions(step=200, include=[SECRET_SETTINGS.start_positions])

        discovered = discover_key(
            KNOWN_PLAINTEXT,
            ciphertext,
            available_rotors=("I", "III", "V"),
            start_position_candidates=candidates,
        )

        self.assertEqual(discovered.rotor_names, SECRET_SETTINGS.rotor_names)
        self.assertEqual(discovered.start_positions, SECRET_SETTINGS.start_positions)
        self.assertEqual(
            set(discovered.plugboard_pairs), set(SECRET_SETTINGS.plugboard_pairs)
        )
        self.assertTrue(discovered.fully_verified)

    def test_rejects_mismatched_lengths(self):
        with self.assertRaises(ValueError):
            discover_key("HELLOWORLD", "TOOSHORT")

    def test_rejects_plaintext_shorter_than_crib_length(self):
        with self.assertRaises(ValueError):
            discover_key("SHORT", "SHORT", crib_length=16)

    def test_raises_when_no_stop_survives(self):
        # A crib that doesn't match the ciphertext at all should be
        # rejected, with no candidate found (rather than a wrong answer).
        ciphertext = EnigmaMachine(SECRET_SETTINGS).encrypt_message(KNOWN_PLAINTEXT)
        wrong_plaintext = "Z" * len(KNOWN_PLAINTEXT)
        candidates = _sample_positions(step=200, include=[SECRET_SETTINGS.start_positions])

        with self.assertRaises(ValueError):
            discover_key(
                wrong_plaintext,
                ciphertext,
                available_rotors=("I", "III", "V"),
                start_position_candidates=candidates,
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
