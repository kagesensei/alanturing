# Alan Turing: A Tribute in Code

A personal project recreating Turing's work in Python — Turing Machine concepts,
Enigma/cryptanalysis, and advanced/quantum-inspired extensions — built roadmap
item by item. See `README.md` for the full roadmap and its background.

## Environment

- Python **3.12** is required (the system default `python` here is 3.7.6 and
  cannot run this code — it lacks `tuple[...]` generic syntax).
- A project-root venv lives at `.venv` (already gitignored). Activate it
  before running or testing anything:
  ```
  # Windows (PowerShell)
  .venv\Scripts\Activate.ps1
  # Windows (Git Bash)
  source .venv/Scripts/activate
  ```
- Activation doesn't persist across separate tool calls/terminals — reactivate
  each new shell session, or chain `activate && command` in one call.
- `.idea/` (PyCharm) and `.venv/` are gitignored — never stage them.
- Dev tooling (currently just Pylint) is pinned in `requirements-dev.txt`;
  install with `pip install -r requirements-dev.txt` after activating.

## Project structure convention

Each roadmap item gets its own self-contained folder (e.g. under
`turing_machines/`), following the pattern set by `basic_simulator` and
`universal_turing_machine`:

- Implementation module + a small demo script.
- `unittest`-based tests (`python -m unittest -v`), run and passing before
  considering the item done.
- Lint-clean under Pylint (see Coding standards below) before considering
  the item done.
- A per-project `README.md` with usage docs.
- Standard library only, unless a future item genuinely needs a dependency.

Prefer this per-folder structure over flat top-level scripts (e.g.
`tm_addition.py`) — it scales better with tests + docs per project.

**Exception — genuine engine reuse:** items that are inherently built on
another item's engine (e.g. everything under `cryptanalysis/` that drives
the Enigma machine: `brute_force_cracker`, `bombe_simulator`,
`automated_key_discovery`, and `bonus/enigma_gui`) should import that
engine rather than duplicate crypto-critical logic across folders.
`brute_force_cracker` imports `enigma_simulator/enigma.py` via a
`sys.path` addition (see the top of `brute_force_cracker.py`);
`.pylintrc`'s `init-hook` mirrors that so Pylint resolves it too. This is
different from the TM modules' *incidental* duplication (a shared
`Direction` enum, etc.), which stays duplicated because those modules are
genuinely independent of each other.

**Exception — runtime dependencies for GUI/app-style items:** the user is
a Flask person, not Django — any web-app-style roadmap item (e.g.
`bonus/enigma_gui`) is a Flask app. These items pin their own runtime
deps in a per-project `requirements.txt` (`pip install -r
requirements.txt` from inside that project's folder), separate from the
root `requirements-dev.txt` (Pylint, shared across the whole repo) —
since Flask/etc. are only needed by that one project, not the repo as a
whole, even though everything still installs into the one shared root
`.venv`.

## Coding standards

Code here needs to stay stable and easy to maintain, so it follows the
spirit of NASA's "Power of 10" rules for safety-critical code, adapted to
Python:

1. **Avoid complex control flow.** No `goto`-equivalents; use recursion only
   when the recursion depth is small and provably bounded (e.g. tree-shaped
   data), not for open-ended/self-referential logic.
2. **Bound every loop.** Prefer `for` over `while`; any `while` loop needs an
   explicit, obviously-reachable exit condition or a `max_steps`-style
   iteration cap (as the TM simulators already do) — no unbounded `while True`.
3. **Keep data scope minimal.** No module-level mutable state; pass data
   explicitly instead of reaching for globals/nonlocal.
4. **Keep functions short — roughly one printed page.** Enforced via Pylint's
   `max-statements`/`max-branches`/`max-nested-blocks` in `.pylintrc`. Split
   a function rather than let it grow past that.
5. **Validate inputs at function boundaries.** Raise (`ValueError`, `assert`
   for internal invariants) on invalid state early, rather than letting bad
   data propagate silently.
6. **Never ignore a return value or a caught exception silently.** Handle it,
   propagate it, or explicitly note why it's safe to ignore.
7. **Avoid clever metaprogramming** (dynamic `exec`/`eval`, metaclasses,
   monkey-patching) — keep control flow readable and statically analyzable.
8. **Limit attribute/indirection chains** (e.g. `a.b.c.d`) — keep object
   graphs shallow.
9. **Run static analysis on everything, and treat warnings as real.** This is
   what Pylint enforces here — see below.

### Linting (Pylint)

- Pylint is a required part of "done," alongside unit tests. Dev tooling
  (`pylint` and its deps) is pinned in `requirements-dev.txt` — install with
  `pip install -r requirements-dev.txt` inside the activated venv.
- Config lives in the root `.pylintrc` (applies repo-wide; tuned toward the
  Power-of-10 limits above — e.g. `max-statements=60`, `max-branches=10`).
- Before considering any module done, run `pylint <path>` and fix real
  findings (unused variables, shadowed names, overlong functions, etc.).
- Known, accepted exception: `duplicate-code` (R0801) findings between TM
  modules are expected and left as-is — each project folder is deliberately
  self-contained/stdlib-only per the structure convention above, so some
  boilerplate (`Direction` enum, `TMResult`/`Transition` types) is
  intentionally repeated rather than factored into a shared dependency.

## Roadmap tracking

The root `README.md` has the authoritative roadmap checklist, grouped by
section (Turing Machine Concepts, Cryptanalysis & Enigma, Advanced Concepts,
Bonus Projects & Reflections). When a roadmap item is completed:
1. Check it off in the root `README.md`.
2. Link it to its project folder.

## Hugging Face tracking

The user's Hugging Face account (`kageskull`) is used for this project. Any
model, dataset, or space published as part of a roadmap item should be
recorded in `HUGGINGFACE.md` (name, link, which roadmap item it belongs to,
notes) — linked from the root `README.md`. Update it whenever new HF
artifacts are published, the same way `README.md`'s roadmap checklist is
updated when an item is completed.

## Git workflow

- Commit completed work locally as it's finished.
- Do **not** push to `origin/main` unless explicitly asked — push only on a
  direct instruction like "push it."

## Verifying work from other sessions (e.g. cloud/claude.ai sessions)

When pulling in work done elsewhere (merges from claude.ai/code sessions,
etc.), don't just trust the commit message's claims. Verify directly:
- Run the full test suite and confirm the pass counts match what's claimed.
- Spot-check the most novel/error-prone modules by running their demos
  directly, not just their tests.
- Confirm the README roadmap was updated correctly.
