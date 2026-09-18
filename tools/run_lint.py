"""Run Pylint, allowing only reviewed duplicate blocks and informational notices."""

import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

from run_tests import PROJECT_ROOTS, ROOT


def duplicate_fingerprint(message: str) -> str:
    """Ignore line-number movement, retaining module identities and exact code."""
    spans = re.findall(r"^==([^:]+):\[(\d+):(\d+)\]", message, re.MULTILINE)
    blocks = []
    for name, start, end in spans:
        matches = [path for group in PROJECT_ROOTS for path in (ROOT / group).rglob(f"{name}.py")]
        if len(matches) != 1:
            break
        source = matches[0].read_text(encoding="utf-8").splitlines()[int(start):int(end)]
        blocks.append(name + '\n' + '\n'.join(source))
    if spans and len(blocks) == len(spans):
        return hashlib.sha256('\n'.join(sorted(blocks)).encode('utf-8')).hexdigest()
    normalized = re.sub(r":\[\d+:\d+\]", "", message.replace("\r\n", "\n"))
    normalized = '\n'.join(line.strip() for line in normalized.splitlines()).strip()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def is_tm_duplicate(message: str) -> bool:
    """Apply the established TM-only exception, rejecting ambiguous module names."""
    names = re.findall(r"^==([^:]+):", message, re.MULTILINE)
    if not names:
        return False
    for name in names:
        matches = [path for group in PROJECT_ROOTS for path in (ROOT / group).rglob(f"{name}.py")]
        if not matches or any(path.relative_to(ROOT).parts[0] != "turing_machines"
                              for path in matches):
            return False
    return True


def is_accepted(finding: dict, baseline: dict) -> bool:
    if finding["type"] == "info":
        return True
    return (
        finding["message-id"] == "R0801"
        and (is_tm_duplicate(finding["message"])
             or duplicate_fingerprint(finding["message"]) in baseline)
    )


def main() -> int:
    baseline_path = Path(__file__).with_name("lint_duplicates.json")
    baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
    targets = [name for name in PROJECT_ROOTS if (ROOT / name).exists()]
    targets.append("test_all.py")
    result = subprocess.run(
        [sys.executable, "-m", "pylint", *targets, "--output-format=json",
         "--reports=n", "--score=n"],
        cwd=ROOT, capture_output=True, text=True, encoding="utf-8", check=False, timeout=300,
    )
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    try:
        findings = json.loads(result.stdout)
    except json.JSONDecodeError:
        print(result.stdout, file=sys.stderr)
        return 1
    failures = [finding for finding in findings if not is_accepted(finding, baseline)]
    for finding in failures:
        print(f"{finding['path']}:{finding['line']}: "
              f"{finding['message-id']} {finding['message']}")
    accepted = sum(finding["message-id"] == "R0801" for finding in findings) - sum(
        finding["message-id"] == "R0801" for finding in failures
    )
    print(f"Pylint: {len(failures)} unaccepted findings; {accepted} reviewed duplicate blocks.")
    # Fatal/usage failures cannot be hidden by an empty or incomplete JSON report.
    return 1 if failures or result.returncode & (1 | 32) else 0


if __name__ == "__main__":
    sys.exit(main())
