import unittest

from enigma import ALPHABET, EnigmaMachine, EnigmaSettings, Plugboard, Reflector, Rotor


class TestRotor(unittest.TestCase):
    def test_rejects_unknown_rotor(self):
        with self.assertRaises(ValueError):
            Rotor("VI")

    def test_rejects_invalid_ring_setting(self):
        with self.assertRaises(ValueError):
            Rotor("I", ring_setting="1")

    def test_at_notch(self):
        rotor = Rotor("I", start_position="Q")
        self.assertTrue(rotor.at_notch())

    def test_step_wraps_around(self):
        rotor = Rotor("I", start_position="Z")
        rotor.step()
        self.assertEqual(rotor.position, 0)

    def test_forward_backward_are_inverse(self):
        rotor = Rotor("III", ring_setting="F", start_position="Q")
        for index in range(26):
            self.assertEqual(rotor.backward(rotor.forward(index)), index)


class TestReflector(unittest.TestCase):
    def test_rejects_unknown_reflector(self):
        with self.assertRaises(ValueError):
            Reflector("Z")

    def test_reflect_has_no_fixed_points(self):
        # A real reflector never maps a contact back to itself.
        reflector = Reflector("B")
        for index in range(26):
            self.assertNotEqual(reflector.reflect(index), index)

    def test_reflect_is_an_involution(self):
        reflector = Reflector("B")
        for index in range(26):
            self.assertEqual(reflector.reflect(reflector.reflect(index)), index)


class TestPlugboard(unittest.TestCase):
    def test_default_is_identity(self):
        plugboard = Plugboard()
        for letter in "ABCXYZ":
            self.assertEqual(plugboard.swap(letter), letter)

    def test_swaps_paired_letters(self):
        plugboard = Plugboard((("A", "B"),))
        self.assertEqual(plugboard.swap("A"), "B")
        self.assertEqual(plugboard.swap("B"), "A")

    def test_rejects_self_pair(self):
        with self.assertRaises(ValueError):
            Plugboard((("A", "A"),))

    def test_rejects_letter_reused_across_pairs(self):
        with self.assertRaises(ValueError):
            Plugboard((("A", "B"), ("B", "C")))


class TestEnigmaMachine(unittest.TestCase):
    def test_requires_three_rotors(self):
        with self.assertRaises(ValueError):
            EnigmaMachine(EnigmaSettings(rotor_names=("I", "II")))

    def test_rejects_duplicate_rotors(self):
        with self.assertRaises(ValueError):
            EnigmaMachine(EnigmaSettings(rotor_names=("I", "I", "III")))

    def test_known_reference_vector(self):
        # Rotors I,II,III / reflector B / ring AAA / start AAA / no plugboard:
        # a widely published Enigma I reference test vector.
        settings = EnigmaSettings(rotor_names=("I", "II", "III"))
        machine = EnigmaMachine(settings)
        self.assertEqual(machine.encrypt_message("AAAAA"), "BDZGO")

    def test_encryption_is_its_own_inverse(self):
        settings = EnigmaSettings(
            rotor_names=("III", "I", "II"),
            ring_settings=("B", "U", "L"),
            start_positions=("X", "Y", "Z"),
            plugboard_pairs=(("A", "M"), ("F", "I"), ("N", "V")),
        )
        plaintext = "THEQUICKBROWNFOXJUMPSOVERTHELAZYDOG"

        ciphertext = EnigmaMachine(settings).encrypt_message(plaintext)
        recovered = EnigmaMachine(settings).encrypt_message(ciphertext)

        self.assertEqual(recovered, plaintext)
        self.assertNotEqual(ciphertext, plaintext)

    def test_never_encrypts_a_letter_to_itself(self):
        # A structural property of the Enigma reflector, and useful for
        # cryptanalysis later in the roadmap.
        settings = EnigmaSettings(rotor_names=("I", "II", "III"))
        machine = EnigmaMachine(settings)
        for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" * 3:
            self.assertNotEqual(machine.encrypt_letter(letter), letter)

    def test_non_letters_are_dropped(self):
        settings = EnigmaSettings(rotor_names=("I", "II", "III"))
        with_punctuation = EnigmaMachine(settings).encrypt_message("A B, c!")
        letters_only = EnigmaMachine(settings).encrypt_message("ABC")
        self.assertEqual(with_punctuation, letters_only)

    def test_double_step_anomaly(self):
        # When the middle rotor sits at its own notch, the very next
        # keypress steps the left rotor too, not just middle/right --
        # rotor II's notch is "E", so it drags rotor I along with it
        # instead of waiting for the usual carry from the right rotor.
        # This is the well-known Enigma "double-stepping" quirk.
        settings = EnigmaSettings(
            rotor_names=("I", "II", "III"), start_positions=("A", "E", "A")
        )
        machine = EnigmaMachine(settings)
        left, middle, right = machine.rotors

        machine.encrypt_letter("A")

        self.assertEqual(left.position, ALPHABET.index("B"))
        self.assertEqual(middle.position, ALPHABET.index("F"))
        self.assertEqual(right.position, ALPHABET.index("B"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
