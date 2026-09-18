"""Bridge standard root unittest discovery to isolated project suites."""

from tools.run_tests import repository_suite


def load_tests(_loader, _tests, _pattern):
    return repository_suite()
