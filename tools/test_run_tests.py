from pathlib import Path
import tempfile
import unittest

from run_tests import project_directories, run_project


class TestRepositoryRunner(unittest.TestCase):
    def test_discovers_nested_project_once(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            project = root / "bonus" / "example"
            project.mkdir(parents=True)
            for name in ("test_one.py", "test_two.py"):
                (project / name).write_text("", encoding="utf-8")
            self.assertEqual(project_directories(root), [project])

    def test_rejects_empty_suite(self):
        with tempfile.TemporaryDirectory() as temporary:
            self.assertNotEqual(run_project(Path(temporary)).returncode, 0)

    def test_propagates_pass_failure_import_error_and_skip(self):
        bodies = (
            ("self.assertTrue(True)", True),
            ("self.fail('intentional failure')", False),
            ("import missing_runner_fixture_dependency", False),
            ("self.skipTest('not available')", False),
        )
        for body, succeeds in bodies:
            with self.subTest(body=body), tempfile.TemporaryDirectory() as temporary:
                directory = Path(temporary)
                (directory / "test_example.py").write_text(
                    "import unittest\nclass Example(unittest.TestCase):\n"
                    f"    def test_example(self):\n        {body}\n", encoding="utf-8",
                )
                self.assertEqual(not run_project(directory).returncode, succeeds)


if __name__ == "__main__":
    unittest.main(verbosity=2)
