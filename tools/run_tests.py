"""Run each self-contained project's unittest suite in a fresh interpreter."""

from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOTS = (
    "turing_machines", "cryptanalysis", "advanced_concepts", "bonus", "persona",
    "tools", "finetune",
)
CHILD = """
import sys, unittest
suite = unittest.defaultTestLoader.discover('.')
if suite.countTestCases() == 0:
    sys.exit('ERROR: no tests discovered')
result = unittest.TextTestRunner(verbosity=2).run(suite)
sys.exit(0 if result.wasSuccessful() and not result.skipped else 1)
"""


def project_directories(root: Path = ROOT) -> list[Path]:
    """Discover test folders without walking environments or hidden directories."""
    return sorted({
        path.parent
        for name in PROJECT_ROOTS
        for path in (root / name).rglob("test_*.py")
        if not any(part.startswith(".") or part == "__pycache__" for part in path.parts)
    })


def run_project(directory: Path, timeout: int = 300) -> subprocess.CompletedProcess:
    """Missing dependencies, skipped tests, empty suites and failures all fail."""
    return subprocess.run(
        [sys.executable, "-c", CHILD], cwd=directory,
        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout,
        check=False,
    )


class ProjectTests(unittest.TestCase):
    """One unittest wrapper per folder; child output reports actual test counts."""

    def __init__(self, directory: Path):
        super().__init__("test_project")
        self.directory = directory

    def shortDescription(self):
        return str(self.directory.relative_to(ROOT))

    def test_project(self):
        result = run_project(self.directory)
        output = result.stdout + result.stderr
        print(output, end="", flush=True)
        self.assertEqual(result.returncode, 0, output)


def repository_suite() -> unittest.TestSuite:
    directories = project_directories()
    if not directories:
        raise ValueError("No project test directories discovered")
    return unittest.TestSuite(ProjectTests(directory) for directory in directories)


if __name__ == "__main__":
    report = unittest.TextTestRunner(verbosity=2).run(repository_suite())
    sys.exit(0 if report.wasSuccessful() else 1)
