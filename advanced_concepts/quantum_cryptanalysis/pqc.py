"""FIPS 203/204/205 post-quantum cryptography: the defensive counterpart
to the Shor's/Grover's algorithm demos elsewhere in this module -- the
NIST-standardized classical algorithms designed to resist attack even
from a large quantum computer.

- FIPS 203 (ML-KEM): lattice-based key encapsulation -- what a quantum-
  resistant TLS handshake uses instead of RSA/ECDH, both of which
  Shor's algorithm (see shors_algorithm.py) breaks.
- FIPS 204 (ML-DSA): lattice-based digital signatures -- what replaces
  RSA/ECDSA signatures for the same reason.
- FIPS 205 (SLH-DSA): hash-based digital signatures (standardized as
  SLH-DSA; built on the SPHINCS+ design) -- a conservative alternative
  to ML-DSA whose security rests on hash function properties rather
  than a newer lattice assumption.

None of these primitives are implemented from scratch here -- getting
lattice/hash-based cryptography right is genuinely dangerous to attempt
without extensive review and formal analysis. This wraps `quantcrypt`
(a maintained Python binding for the PQClean reference implementations)
behind a small, consistent API instead.
"""

from __future__ import annotations

from dataclasses import dataclass

from quantcrypt.dss import FAST_SPHINCS, MLDSA_65, DSSVerifyFailedError
from quantcrypt.kem import MLKEM_768


@dataclass
class KeyPair:
    public_key: bytes
    secret_key: bytes


@dataclass
class Encapsulation:
    ciphertext: bytes
    shared_secret: bytes


def ml_kem_keygen() -> KeyPair:
    """FIPS 203: generate an ML-KEM-768 key pair."""
    public_key, secret_key = MLKEM_768().keygen()
    return KeyPair(bytes(public_key), bytes(secret_key))


def ml_kem_encapsulate(public_key: bytes) -> Encapsulation:
    """FIPS 203: derive a shared secret and its ciphertext for `public_key`."""
    ciphertext, shared_secret = MLKEM_768().encaps(public_key)
    return Encapsulation(bytes(ciphertext), bytes(shared_secret))


def ml_kem_decapsulate(secret_key: bytes, ciphertext: bytes) -> bytes:
    """FIPS 203: recover the shared secret from `ciphertext` using `secret_key`."""
    return bytes(MLKEM_768().decaps(secret_key, ciphertext))


def ml_dsa_keygen() -> KeyPair:
    """FIPS 204: generate an ML-DSA-65 key pair."""
    public_key, secret_key = MLDSA_65().keygen()
    return KeyPair(bytes(public_key), bytes(secret_key))


def ml_dsa_sign(secret_key: bytes, message: bytes) -> bytes:
    """FIPS 204: sign `message` with `secret_key`."""
    return bytes(MLDSA_65().sign(secret_key, message))


def ml_dsa_verify(public_key: bytes, message: bytes, signature: bytes) -> bool:
    """FIPS 204: verify `signature` over `message` under `public_key`.

    quantcrypt raises DSSVerifyFailedError rather than returning False on
    a bad signature -- this normalizes that into a plain boolean.
    """
    try:
        return MLDSA_65().verify(public_key, message, signature)
    except DSSVerifyFailedError:
        return False


def slh_dsa_keygen() -> KeyPair:
    """FIPS 205: generate an SLH-DSA (SPHINCS+, "fast" parameter set) key pair."""
    public_key, secret_key = FAST_SPHINCS().keygen()
    return KeyPair(bytes(public_key), bytes(secret_key))


def slh_dsa_sign(secret_key: bytes, message: bytes) -> bytes:
    """FIPS 205: sign `message` with `secret_key`."""
    return bytes(FAST_SPHINCS().sign(secret_key, message))


def slh_dsa_verify(public_key: bytes, message: bytes, signature: bytes) -> bool:
    """FIPS 205: verify `signature` over `message` under `public_key`."""
    try:
        return FAST_SPHINCS().verify(public_key, message, signature)
    except DSSVerifyFailedError:
        return False


if __name__ == "__main__":
    print("FIPS 203 (ML-KEM-768): key encapsulation")
    kem_keys = ml_kem_keygen()
    encapsulation = ml_kem_encapsulate(kem_keys.public_key)
    recovered_secret = ml_kem_decapsulate(kem_keys.secret_key, encapsulation.ciphertext)
    print(f"  shared secrets match: {encapsulation.shared_secret == recovered_secret}")

    print("FIPS 204 (ML-DSA-65): digital signatures")
    dsa_keys = ml_dsa_keygen()
    dsa_message = b"Turing would have loved post-quantum cryptography"
    dsa_signature = ml_dsa_sign(dsa_keys.secret_key, dsa_message)
    dsa_valid = ml_dsa_verify(dsa_keys.public_key, dsa_message, dsa_signature)
    dsa_tampered_rejected = not ml_dsa_verify(
        dsa_keys.public_key, dsa_message + b"!", dsa_signature
    )
    print(f"  genuine signature verifies: {dsa_valid}")
    print(f"  tampered message rejected: {dsa_tampered_rejected}")

    print("FIPS 205 (SLH-DSA / SPHINCS+): hash-based digital signatures")
    slh_keys = slh_dsa_keygen()
    slh_signature = slh_dsa_sign(slh_keys.secret_key, dsa_message)
    slh_valid = slh_dsa_verify(slh_keys.public_key, dsa_message, slh_signature)
    print(f"  genuine signature verifies: {slh_valid}")
