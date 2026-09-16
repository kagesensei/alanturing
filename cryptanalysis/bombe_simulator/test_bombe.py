import itertools
import unittest

from bombe import ALPHABET, find_bombe_stops
from enigma import EnigmaMachine, EnigmaSettings

SECRET_SETTINGS = EnigmaSettings(
    rotor_names=("II", "I", "III"),
    start_positions=("B", "R", "U"),
    plugboard_pairs=(("A", "M"), ("F", "I"), ("N", "V")),
)
CRIB = "ATTACKATDAWN"
PLAINTEXT = "ATTACKATDAWNNEARTHEBRIDGEATTACKATDAWN"


def _sample_positions(step, include):
    """Every `step`-th of the 17,576 start positions (fast to search),
    plus whatever's in `include` -- keeps tests from having to run the
    full (slow) exhaustive search while still exercising real pruning.
    """
    positions = list(itertools.product(ALPHABET, repeat=3))[::step]
    for extra in include:
        if extra not in positions:
            positions.append(extra)
    return positions


class TestFindBombeStops(unittest.TestCase):
    def test_true_setting_is_always_among_the_stops(self):
        # The correct rotor order/position necessarily satisfies its own
        # menu, so it must never be rejected as a false negative.
        ciphertext = EnigmaMachine(SECRET_SETTINGS).encrypt_message(PLAINTEXT)
        candidates = _sample_positions(step=300, include=[SECRET_SETTINGS.start_positions])

        stops = find_bombe_stops(
            ciphertext,
            CRIB,
            available_rotors=("I", "II", "III"),
            start_position_candidates=candidates,
        )

        matches = [
            stop
            for stop in stops
            if stop.rotor_names == SECRET_SETTINGS.rotor_names
            and stop.start_positions == SECRET_SETTINGS.start_positions
        ]
        self.assertEqual(len(matches), 1)

    def test_sampled_search_prunes_almost_everything(self):
        # A deterministic regression check on real pruning power: out of
        # 6 rotor orders x 89 sampled positions (534 candidates), only
        # the true setting should survive as a stop.
        ciphertext = EnigmaMachine(SECRET_SETTINGS).encrypt_message(PLAINTEXT)
        candidates = _sample_positions(step=200, include=[SECRET_SETTINGS.start_positions])

        stops = find_bombe_stops(
            ciphertext,
            CRIB,
            available_rotors=("I", "II", "III"),
            start_position_candidates=candidates,
        )

        self.assertEqual(len(stops), 1)
        self.assertEqual(stops[0].rotor_names, SECRET_SETTINGS.rotor_names)
        self.assertEqual(stops[0].start_positions, SECRET_SETTINGS.start_positions)

    def test_recovered_plugboard_matches_the_true_one_where_connected(self):
        ciphertext = EnigmaMachine(SECRET_SETTINGS).encrypt_message(PLAINTEXT)

        stops = find_bombe_stops(
            ciphertext,
            CRIB,
            available_rotors=("I", "II", "III"),
            start_position_candidates=[SECRET_SETTINGS.start_positions],
        )

        self.assertEqual(len(stops), 1)
        true_partner = {"A": "M", "M": "A", "F": "I", "I": "F", "N": "V", "V": "N"}
        for letter, partner in stops[0].plugboard.items():
            self.assertEqual(partner, true_partner.get(letter, letter))

    def test_rejects_empty_crib(self):
        with self.assertRaises(ValueError):
            find_bombe_stops("ABCDE", crib="")

    def test_rejects_non_letter_crib(self):
        with self.assertRaises(ValueError):
            find_bombe_stops("ABCDE", crib="AB1")

    def test_rejects_crib_longer_than_ciphertext(self):
        with self.assertRaises(ValueError):
            find_bombe_stops("ABC", crib="ABCDE")


if __name__ == "__main__":
    unittest.main(verbosity=2)
