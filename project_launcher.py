"""Run the project catalogue and the Turing Test chat in one local Flask process."""

from pathlib import Path
import sys

from flask import Flask, redirect, render_template
from werkzeug.middleware.dispatcher import DispatcherMiddleware


ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'bonus' / 'turing_test_simulator'))
from simulator_app import create_app as create_chat  # pylint: disable=wrong-import-position


PROJECTS = (
    ('Turing Machine Concepts',
     'Basic Turing Machine',
     'Tape transitions, binary increment and complement.'),
    ('Turing Machine Concepts',
     'Universal Turing Machine',
     'A machine that interprets encoded machines.'),
    ('Turing Machine Concepts',
     'Non-Deterministic Turing Machine',
     'Explore branching computational paths.'),
    ('Turing Machine Concepts',
     'Arithmetic Turing Machine',
     'Perform arithmetic through tape operations.'),
    ('Turing Machine Concepts',
     'Palindrome Turing Machine',
     'Recognize strings that read the same backwards.'),
    ('Turing Machine Concepts',
     'Self-Replicating Turing Machine',
     'Copy an encoded machine description.'),
    ('Cryptanalysis & Enigma',
     'Enigma Simulator',
     'Recreate rotors, reflectors and plugboard encryption.'),
    ('Cryptanalysis & Enigma',
     'Brute Force Enigma Cracker',
     'Search Enigma settings using known plaintext.'),
    ('Cryptanalysis & Enigma',
     'Frequency Analysis',
     'Analyze letter frequencies and classical ciphers.'),
    ('Cryptanalysis & Enigma',
     'Bombe Simulator',
     'Explore constraint-based Enigma key elimination.'),
    ('Cryptanalysis & Enigma',
     'Automated Key Discovery',
     'Recover and verify rotor and plugboard settings.'),
    ('Cryptanalysis & Enigma',
     'Lorenz Cipher',
     'Simulate teleprinter encryption and known-plaintext recovery.'),
    ('Advanced Concepts',
     'Quantum-Inspired Cryptanalysis',
     'Explore toy factoring and quantum backends.'),
    ('Advanced Concepts',
     'Cellular Automaton',
     'Explore computation through evolving grids of cells.'),
    ('Advanced Concepts',
     'Genetic Codebreaker',
     'Search substitution keys with evolutionary algorithms.'),
    ('Bonus Projects',
     'Turing Test Simulator',
     'Chat with turing-a1 and compare machine and human replies.'),
    ('Bonus Projects', 'Enigma GUI', 'Configure and inspect an Enigma machine visually.'),
    ('Bonus Projects', 'Historical Notes', 'Personal reflections on Turing and this collection.'),
    ('Supporting Projects',
     'Historical Persona',
     'Explore source-backed historical evidence and cutoffs.'),
    ('Supporting Projects',
     'turing-a1 Fine-Tuning',
     'Train and evaluate local computational-reasoning adapters.'),
)


def create_app(conversation=None):
    app = Flask(__name__, static_folder=None)

    @app.get('/')
    def index():
        return render_template('projects.html', projects=PROJECTS)

    @app.get('/chat')
    def chat_redirect():
        return redirect('/chat/')

    chat = create_chat(conversation)
    app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {'/chat': chat})
    return app
