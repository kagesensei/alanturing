import unittest

from app import _parse_plugboard, app

# Importing `app` already adds enigma_simulator to sys.path as a side
# effect (see app.py), so this import can rely on that rather than
# repeating the sys.path setup here.
from enigma import EnigmaMachine, EnigmaSettings

VALID_FORM = {
    "rotor1": "I",
    "rotor2": "II",
    "rotor3": "III",
    "ring1": "A",
    "ring2": "A",
    "ring3": "A",
    "start1": "A",
    "start2": "A",
    "start3": "A",
    "reflector": "B",
    "plugboard": "AB CD",
    "message": "HELLO WORLD",
}


class TestParsePlugboard(unittest.TestCase):
    def test_parses_pairs(self):
        self.assertEqual(_parse_plugboard("AB CD"), (("A", "B"), ("C", "D")))

    def test_empty_string_is_no_pairs(self):
        self.assertEqual(_parse_plugboard(""), ())

    def test_rejects_wrong_length_token(self):
        with self.assertRaises(ValueError):
            _parse_plugboard("ABC")

    def test_lowercase_is_uppercased(self):
        self.assertEqual(_parse_plugboard("ab"), (("A", "B"),))


class TestEnigmaGuiRoutes(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_index_page_loads(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"<form", response.data)

    def test_encrypt_matches_direct_engine_call(self):
        response = self.client.post("/encrypt", data=VALID_FORM)
        self.assertEqual(response.status_code, 200)

        expected_settings = EnigmaSettings(
            rotor_names=("I", "II", "III"),
            ring_settings=("A", "A", "A"),
            start_positions=("A", "A", "A"),
            reflector_name="B",
            plugboard_pairs=(("A", "B"), ("C", "D")),
        )
        expected_ciphertext = EnigmaMachine(expected_settings).encrypt_message("HELLO WORLD")

        self.assertIn(expected_ciphertext.encode(), response.data)

    def test_encrypt_round_trips_through_two_requests(self):
        first = self.client.post("/encrypt", data=VALID_FORM)
        self.assertEqual(first.status_code, 200)

        # Extract the ciphertext the same way the direct-engine test does,
        # to feed it back through a second, independent request.
        expected_settings = EnigmaSettings(
            rotor_names=("I", "II", "III"),
            ring_settings=("A", "A", "A"),
            start_positions=("A", "A", "A"),
            reflector_name="B",
            plugboard_pairs=(("A", "B"), ("C", "D")),
        )
        ciphertext = EnigmaMachine(expected_settings).encrypt_message("HELLO WORLD")

        second_form = dict(VALID_FORM, message=ciphertext)
        second = self.client.post("/encrypt", data=second_form)
        self.assertIn(b"HELLOWORLD", second.data)

    def test_duplicate_rotors_shows_error_not_500(self):
        form = dict(VALID_FORM, rotor2="I")
        response = self.client.post("/encrypt", data=form)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"distinct", response.data)

    def test_malformed_plugboard_shows_error_not_500(self):
        form = dict(VALID_FORM, plugboard="ABC")
        response = self.client.post("/encrypt", data=form)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"error", response.data.lower())

    def test_missing_form_field_shows_error_not_500(self):
        incomplete = dict(VALID_FORM)
        del incomplete["reflector"]
        response = self.client.post("/encrypt", data=incomplete)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"error", response.data.lower())


if __name__ == "__main__":
    unittest.main(verbosity=2)
