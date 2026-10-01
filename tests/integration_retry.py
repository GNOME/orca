"""Runs integration tests with one CI-only retry for assertion failures."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pytest


class AttemptReport:
    """Records assertion failures separately from errors and expected failures."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.failed: list[str] = []
        self.passed: list[str] = []
        self.assertions: set[str] = set()
        self.blocked = False

    def pytest_runtest_makereport(self, item: pytest.Item, call: pytest.CallInfo) -> None:
        """Identifies assertion failures in the test body."""

        if (
            call.when == "call"
            and call.excinfo is not None
            and call.excinfo.errisinstance(AssertionError)
        ):
            self.assertions.add(item.nodeid)

    def pytest_runtest_logreport(self, report: pytest.TestReport) -> None:
        """Records the final result after pytest's xfail handling."""

        if report.failed:
            if (
                report.when == "call"
                and report.nodeid in self.assertions
                and not hasattr(report, "wasxfail")
            ):
                self.failed.append(report.nodeid)
            else:
                self.blocked = True
        elif report.when == "call" and report.passed:
            self.passed.append(report.nodeid)

    def pytest_sessionfinish(self, session: pytest.Session) -> None:
        """Writes the outcome even when pytest reports a nonzero exit status."""

        self.path.write_text(
            json.dumps(
                {
                    "failed": self.failed,
                    "passed": self.passed,
                    "blocked": self.blocked,
                    "root": str(session.config.rootpath),
                }
            ),
            encoding="utf-8",
        )


def _attempt(
    selectors: list[str],
    report: Path,
    log: Path,
    cwd: str | None = None,
    *,
    env: dict[str, str] | None = None,
) -> tuple[int, dict]:
    """Runs pytest in a fresh process and retains its output."""

    with log.open("w", encoding="utf-8") as output:
        result = subprocess.run(
            [sys.executable, __file__, "--attempt", str(report), *selectors],
            stdout=output,
            stderr=subprocess.STDOUT,
            cwd=cwd,
            env=env,
            check=False,
        )
    with log.open(encoding="utf-8") as output:
        shutil.copyfileobj(output, sys.stdout)
    sys.stdout.flush()
    data = json.loads(report.read_text(encoding="utf-8")) if report.exists() else {}
    return result.returncode, data


def _run(test_file: str, directory: Path) -> int:
    """Retries only failed assertions, after the first pytest session has ended."""

    directory.mkdir(parents=True, exist_ok=True)
    name = Path(test_file).stem
    first_log = directory / f"{name}.first.log"
    retry_log = directory / f"{name}.retry.log"
    summary = directory / f"{name}.summary"
    debug_archive = directory / f"{name}.orca-debug.tar.gz"
    summary.unlink(missing_ok=True)
    retry_log.unlink(missing_ok=True)
    debug_archive.unlink(missing_ok=True)
    with tempfile.TemporaryDirectory(prefix="orca-retry-") as temporary:
        code, first = _attempt([test_file], Path(temporary) / "first.json", first_log)
        if code == 0 and first:
            first_log.unlink()
            return 0
        if code != 1 or first.get("blocked") or not first.get("failed"):
            return code or 1
        failed = first["failed"]
        print(f"Retrying {len(failed)} failed test(s) once with fresh fixtures.", flush=True)
        debug_dir = Path(temporary) / "orca-debug"
        retry_env = os.environ.copy()
        retry_env.pop("ORCA_TEST_DEBUG_FILE", None)
        retry_env["ORCA_TEST_DEBUG_DIR"] = str(debug_dir)
        code, second = _attempt(
            failed, Path(temporary) / "retry.json", retry_log, first["root"], env=retry_env
        )
        passed = (
            set(second.get("passed", [])) if code in (0, 1) and not second.get("blocked") else set()
        )
        lines = [
            f"{'PASSED ON RETRY' if node in passed else 'FAILED ON RETRY'}: {node}"
            for node in failed
        ]
        if second.get("blocked") or code not in (0, 1):
            lines.append("Retry encountered an error; the test file remains failed.")
        recovered = code == 0 and set(failed) <= passed
        if not recovered and debug_dir.is_dir():
            shutil.make_archive(str(directory / f"{name}.orca-debug"), "gztar", debug_dir)
            lines.append(f"Orca retry debug logs: {debug_archive}")
        text = "\n".join(lines) + "\n"
        summary.write_text(text, encoding="utf-8")
        print(text, end="", flush=True)
        return 0 if recovered else 1


def main() -> int:
    """Runs a file, a single attempt, or prints the CI retry summary."""

    args = sys.argv[1:]
    if args[0] == "--attempt":
        import pytest

        return int(pytest.main([*args[2:], "-v"], plugins=[AttemptReport(Path(args[1]))]))
    if args[0] == "--summary":
        summaries = sorted(Path(args[1]).glob("*.summary"))
        print("Integration test retries:" if summaries else "No integration tests were retried.")
        for summary in summaries:
            print(summary.read_text(encoding="utf-8"), end="")
        return 0
    directory = os.environ.get("ORCA_TEST_RETRY_DIR")
    if directory:
        return _run(args[0], Path(directory))
    os.execv(sys.executable, [sys.executable, "-m", "pytest", args[0], "-v"])  # noqa: S606
    return 1


if __name__ == "__main__":
    sys.exit(main())
