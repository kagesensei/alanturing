import unittest

from brute_force_cracker import CrackResult, EnigmaMachine, EnigmaSettings, crack


class TestCrack(unittest.TestCase):
    def test_rejects_empty_crib(self):
        with self.assertRaises(ValueError):
            crack("ABCDE", crib="")

    def test_rejects_non_letter_crib(self):
        with self.assertRaises(ValueError):
            crack("ABCDE", crib="AB1")

    def test_rejects_crib_longer_than_ciphertext(self):
        with self.assertRaises(ValueError):
            crack("ABC", crib="ABCDE")

    def test_finds_the_correct_rotor_order_and_start_position(self):
        # Only three rotors in the pool (I, II, III), matching the
        # historical pre-1938 Enigma I -- keeps the search small enough
        # to run quickly while still exercising the full rotor-order and
        # start-position search space.
        settings = EnigmaSettings(rotor_names=("II", "III", "I"), start_positions=("F", "Q", "K"))
        plaintext = "ATTACKATDAWN"
        ciphertext = EnigmaMachine(settings).encrypt_message(plaintext)

        results = crack(
            ciphertext, crib="ATTACKAT", available_rotors=("I", "II", "III")
        )

        self.assertTrue(
            any(
                result.rotor_names == settings.rotor_names
                and result.start_positions == settings.start_positions
                for result in results
            )
        )

    def test_every_match_actually_decrypts_to_something_starting_with_the_crib(self):
        settings = EnigmaSettings(rotor_names=("I", "II", "III"), start_positions=("A", "A", "A"))
        ciphertext = EnigmaMachine(settings).encrypt_message("HELLOWORLD")

        results = crack(ciphertext, crib="HELLO", available_rotors=("I", "II", "III"))

        self.assertTrue(results)
        for result in results:
            self.assertIsInstance(result, CrackResult)
            self.assertTrue(result.decrypted.startswith("HELLO"))

    def test_no_matches_for_a_crib_that_cannot_be_right(self):
        settings = EnigmaSettings(rotor_names=("I", "II", "III"), start_positions=("A", "A", "A"))
        ciphertext = EnigmaMachine(settings).encrypt_message("HELLOWORLD")

        # A letter can never encrypt to itself, so a crib equal to the
        # ciphertext itself is guaranteed to match nothing.
        results = crack(ciphertext, crib=ciphertext[:5], available_rotors=("I", "II", "III"))

        self.assertEqual(results, [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
