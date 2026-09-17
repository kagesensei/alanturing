"""Interactive Flask front-end for the Enigma machine simulator, built
directly on enigma_simulator's tested engine (see the sys.path note below
-- the same "genuine engine reuse" exception documented in CLAUDE.md for
the cryptanalysis modules).
"""

from __future__ import annotations

import json
import logging
import os
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

# One JSON object per line, so a session's usage can be reviewed later --
# not just the bare access log Flask's dev server already prints.
# Gitignored (*.log); this is local runtime data, not source. Overridable
# via ENIGMA_GUI_LOG_PATH so tests don't pollute the real activity log
# with their own fixture requests (the mistake this exact conversation
# caught, reading the log after test runs had already written to it).
_LOG_PATH = Path(
    os.environ.get("ENIGMA_GUI_LOG_PATH", str(Path(__file__).resolve().parent / "activity.log"))
)
activity_logger = logging.getLogger("enigma_gui.activity")
activity_logger.setLevel(logging.INFO)
if not activity_logger.handlers:
    _handler = logging.FileHandler(_LOG_PATH, encoding="utf-8")
    _handler.setFormatter(logging.Formatter("%(message)s"))
    activity_logger.addHandler(_handler)


def _log_encrypt_attempt(form, message: str, result, error: str | None) -> None:
    entry = {
        "rotor_names": [form.get("rotor1"), form.get("rotor2"), form.get("rotor3")],
        "ring_settings": [form.get("ring1"), form.get("ring2"), form.get("ring3")],
        "start_positions": [form.get("start1"), form.get("start2"), form.get("start3")],
        "reflector_name": form.get("reflector"),
        "plugboard": form.get("plugboard", ""),
        "message": message,
        "ciphertext": result.ciphertext if result else None,
        "error": error,
    }
    activity_logger.info(json.dumps(entry))


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


_REQUIRED_FIELDS = (
    "rotor1", "rotor2", "rotor3", "ring1", "ring2", "ring3",
    "start1", "start2", "start3", "reflector",
)


def _require_field(form, field: str) -> str:
    value = form.get(field)
    if not value:
        raise ValueError(f"required field missing: {field!r}")
    return value


def _settings_from_form(form) -> EnigmaSettings:
    for field in _REQUIRED_FIELDS:
        _require_field(form, field)
    return EnigmaSettings(
        rotor_names=(form["rotor1"], form["rotor2"], form["rotor3"]),
        ring_settings=(form["ring1"], form["ring2"], form["ring3"]),
        start_positions=(form["start1"], form["start2"], form["start3"]),
        reflector_name=form["reflector"],
        plugboard_pairs=_parse_plugboard(form.get("plugboard", "")),
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
    message = request.form.get("message", "")
    try:
        settings = _settings_from_form(request.form)
        result = _run_machine(settings, message)
    except (ValueError, KeyError) as exc:
        error = str(exc)

    _log_encrypt_attempt(request.form, message, result, error)

    return render_template(
        "index.html", **_default_context(), form=request.form, error=error, result=result
    )


if __name__ == "__main__":
    app.run(debug=False)
