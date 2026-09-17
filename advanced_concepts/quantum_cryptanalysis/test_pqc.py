import unittest

from pqc import (
    Encapsulation,
    KeyPair,
    ml_dsa_keygen,
    ml_dsa_sign,
    ml_dsa_verify,
    ml_kem_decapsulate,
    ml_kem_encapsulate,
    ml_kem_keygen,
    slh_dsa_keygen,
    slh_dsa_sign,
    slh_dsa_verify,
)


class TestMlKem(unittest.TestCase):
    def test_keygen_returns_distinct_keys(self):
        keys = ml_kem_keygen()
        self.assertIsInstance(keys, KeyPair)
        self.assertNotEqual(keys.public_key, keys.secret_key)

    def test_encapsulate_decapsulate_round_trip(self):
        keys = ml_kem_keygen()
        encapsulation = ml_kem_encapsulate(keys.public_key)
        self.assertIsInstance(encapsulation, Encapsulation)

        recovered = ml_kem_decapsulate(keys.secret_key, encapsulation.ciphertext)
        self.assertEqual(recovered, encapsulation.shared_secret)

    def test_different_keypairs_give_different_shared_secrets(self):
        keys_a = ml_kem_keygen()
        keys_b = ml_kem_keygen()
        secret_a = ml_kem_encapsulate(keys_a.public_key).shared_secret
        secret_b = ml_kem_encapsulate(keys_b.public_key).shared_secret
        self.assertNotEqual(secret_a, secret_b)


class TestMlDsa(unittest.TestCase):
    def test_genuine_signature_verifies(self):
        keys = ml_dsa_keygen()
        message = b"a message worth signing"
        signature = ml_dsa_sign(keys.secret_key, message)
        self.assertTrue(ml_dsa_verify(keys.public_key, message, signature))

    def test_tampered_message_is_rejected(self):
        keys = ml_dsa_keygen()
        message = b"original message"
        signature = ml_dsa_sign(keys.secret_key, message)
        self.assertFalse(ml_dsa_verify(keys.public_key, message + b"!", signature))

    def test_wrong_public_key_is_rejected(self):
        keys = ml_dsa_keygen()
        other_keys = ml_dsa_keygen()
        message = b"a message"
        signature = ml_dsa_sign(keys.secret_key, message)
        self.assertFalse(ml_dsa_verify(other_keys.public_key, message, signature))


class TestSlhDsa(unittest.TestCase):
    def test_genuine_signature_verifies(self):
        keys = slh_dsa_keygen()
        message = b"a hash-based signature"
        signature = slh_dsa_sign(keys.secret_key, message)
        self.assertTrue(slh_dsa_verify(keys.public_key, message, signature))

    def test_tampered_message_is_rejected(self):
        keys = slh_dsa_keygen()
        message = b"original"
        signature = slh_dsa_sign(keys.secret_key, message)
        self.assertFalse(slh_dsa_verify(keys.public_key, message + b"!", signature))


if __name__ == "__main__":
    unittest.main(verbosity=2)
