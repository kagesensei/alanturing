# Repository checks

With the root Python 3.12 environment activated and project dependencies
installed, run `python -m unittest discover -v` from the repository root.
`python tools/run_tests.py` is an equivalent explicit entry point.

Each project runs in a fresh interpreter with its own working directory,
preserving local imports and avoiding module-name collisions. Output includes
each child's real test count; the final unittest count is the number of project
suites. Test folders are discovered beneath `turing_machines`, `cryptanalysis`,
`advanced_concepts`, `bonus`, `persona`, and `tools`.

Empty suites, missing dependencies, skipped tests, failures, and a per-project
300-second timeout fail the check. There is no silent optional-backend skip.
The GitHub Actions workflow runs the same command on Linux and Windows with
Python 3.12. A hosted CI result is available only after pushing the workflow.

Run `python tools/run_lint.py` for the CI lint check. It keeps all Pylint
warnings enabled, ignores informational notices, and preserves the established
exception for duplication wholly within the independent TM projects. Other
duplicates must match reviewed source blocks in `lint_duplicates.json`.
Fingerprints ignore line-number changes, but changed source blocks require review.
Do not regenerate this file blindly to make a failing check pass.

The baseline preserves the established independent-TM convention. Additional
reviewed exceptions cover equivalent quantum-backend tests/results/demo setup,
Lorenz settings data fields, crib validation/settings assembly, and sampled
position test fixtures. These are small contracts or scaffolding; the Enigma
engine remains shared. New duplication and all other warnings fail CI.
