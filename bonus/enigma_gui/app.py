"""Interactive Flask front-end for the Enigma machine simulator, built
directly on enigma_simulator's tested engine (see the sys.path note below
-- the same "genuine engine reuse" exception documented in CLAUDE.md for
the cryptanalysis modules).
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

from flask import Flask, render_template, request

_ENIGMA_SIMULATOR_DIR = (
    Path(__file__).resolve().parent.parent.parent / "cryptanalysis" / "enigma_simulator"
)
if str(_ENIGMA_SIMULATOR_DIR) not in sys.path:
    sys.path.insert(0, str(_ENIGMA_SIMULATOR_DIR))

from enigma import (  # pylint: disable=wrong-import-position
    ALPHABET,
    REFLECTOR_WIRINGS,
    ROTOR_WIRINGS,
    EnigmaMachine,
    EnigmaSettings,
)

app = Flask(__name__)

ROTOR_CHOICES = sorted(ROTOR_WIRINGS)
REFLECTOR_CHOICES = sorted(REFLECTOR_WIRINGS)


@dataclass
class EncryptionResult:
    ciphertext: str
    rotor_positions: list[tuple[int, int, int]]


def _parse_plugboard(raw: str) -> tuple[tuple[str, str], ...]:
    """Parse a plugboard string like "AB CD EF" into pair tuples."""
    pairs = []
    for token in raw.upper().split():
        if len(token) != 2:
            raise ValueError(f"plugboard pair {token!r} must be exactly two letters")
        pairs.append((token[0], token[1]))
    return tuple(pairs)


def _run_machine(settings: EnigmaSettings, message: str) -> EncryptionResult:
    machine = EnigmaMachine(settings)
    letters = [char for char in message.upper() if char in ALPHABET]
    ciphertext_letters = []
    rotor_positions = []
    for letter in letters:
        ciphertext_letters.append(machine.encrypt_letter(letter))
        rotor_positions.append(tuple(rotor.position for rotor in machine.rotors))
    return EncryptionResult("".join(ciphertext_letters), rotor_positions)


def _settings_from_form(form) -> EnigmaSettings:
    rotor_names = (form["rotor1"], form["rotor2"], form["rotor3"])
    ring_settings = (form["ring1"], form["ring2"], form["ring3"])
    start_positions = (form["start1"], form["start2"], form["start3"])
    plugboard_pairs = _parse_plugboard(form.get("plugboard", ""))
    return EnigmaSettings(
        rotor_names=rotor_names,
        ring_settings=ring_settings,
        start_positions=start_positions,
        reflector_name=form["reflector"],
        plugboard_pairs=plugboard_pairs,
    )


def _default_context() -> dict:
    return {
        "rotor_choices": ROTOR_CHOICES,
        "reflector_choices": REFLECTOR_CHOICES,
        "alphabet": ALPHABET,
    }


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", **_default_context())


@app.route("/encrypt", methods=["POST"])
def encrypt():
    error = None
    result = None
    try:
        settings = _settings_from_form(request.form)
        result = _run_machine(settings, request.form.get("message", ""))
    except (ValueError, KeyError) as exc:
        error = str(exc)

    return render_template(
        "index.html", **_default_context(), form=request.form, error=error, result=result
    )


if __name__ == "__main__":
    app.run(debug=False)
