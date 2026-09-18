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
