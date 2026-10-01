"""Compares Chromium integration retries without Orca debug instrumentation."""

# ruff: noqa: INP001, S603, S607, T201

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

_FILES = (
    "test_web_form_fields",
    "test_web_form_state_changes",
    "test_web_dynamic_content",
    "test_web_removed_child_recovery",
    "test_web_option_removal",
)


def main() -> int:
    """Alternates three pairs, retaining each attempt and continuing after failures."""

    project = Path(__file__).resolve().parent.parent
    build = (project / os.environ.get("MESON_BUILD_DIR", "_build")).resolve()
    output = build / "retry-comparison"
    output.mkdir()
    env = os.environ.copy()
    for key in (
        "ORCA_TEST_DEBUG_DIR",
        "ORCA_TEST_DEBUG_FILE",
        "ORCA_TEST_RETRY_DIR",
        "ORCA_TEST_TIMEOUT_SCALE",
        "ORCA_TEST_PROFILE",
        "ORCA_TEST_COVERAGE",
        "ORCA_TEST_BROWSER_BINARY",
        "ORCA_TEST_CHROMIUM_BINARY",
        "PYTEST_ADDOPTS",
    ):
        env.pop(key, None)
    env.update(
        ORCA_TEST_BROWSER="chromium",
        ORCA_TEST_RETRY_DEBUG="0",
        PYTHONPATH=f"{project}:{project / 'src'}",
        GSETTINGS_BACKEND="memory",
        MALLOC_PERTURB_="156",
    )
    env["PYTEST_PLUGINS"] = ",".join(
        filter(None, (env.get("PYTEST_PLUGINS"), "tests.integration_tests.late_output_diagnostics"))
    )
    status = 0
    with (output / "summary.tsv").open("w", encoding="utf-8") as summary:
        summary.write("round\tretries\tfile\texit\tfirst attempt; retry if needed\n")
        for round_number in range(1, 4):
            for mode in ("off", "on") if round_number % 2 else ("on", "off"):
                directory = output / f"{round_number}-{mode}"
                directory.mkdir()
                env["ORCA_TEST_RETRY_DIR"] = str(directory / "retries") if mode == "on" else ""
                for name in _FILES:
                    env["ORCA_TEST_CARET_TRACE"] = "0"
                    env["ORCA_TEST_FOCUS_TRACE"] = (
                        "1"
                        if name
                        in (
                            "test_web_form_fields",
                            "test_web_form_state_changes",
                            "test_web_option_removal",
                        )
                        else "0"
                    )
                    print(f"Round {round_number}, retries {mode}: {name}", flush=True)
                    log = directory / f"{name}.log"
                    with log.open("w", encoding="utf-8") as stream:
                        result = subprocess.run(
                            [
                                "timeout",
                                "--kill-after=10s",
                                "240s",
                                sys.executable,
                                str(build / "tests/integration_test_wrapper.py"),
                                str(project / "tests/integration_tests" / f"{name}.py"),
                            ],
                            cwd=build,
                            env=env,
                            stdout=stream,
                            stderr=subprocess.STDOUT,
                            check=False,
                        )
                    text = log.read_text(encoding="utf-8", errors="replace")
                    outcomes = re.findall(r"^=+ (.*? in .*?) =+$", text, re.MULTILINE)
                    line = (
                        f"{round_number}\t{mode}\t{name}\t{result.returncode}\t"
                        + "; ".join(outcomes)
                        + "\n"
                    )
                    summary.write(line)
                    summary.flush()
                    print(line, end="", flush=True)
                    for detail in text.splitlines():
                        if detail.startswith(
                            (
                                "FAILED ",
                                "PASSED ON RETRY:",
                                "FAILED ON RETRY:",
                                "[late-output]",
                                "[setup-output]",
                                "[caret-trace]",
                                "[focus-trace]",
                            )
                        ):
                            print(detail, flush=True)
                    if result.returncode:
                        status = 1
                    if result.returncode not in (0, 1):
                        print(f"Stopping after wrapper exit {result.returncode}; see {log}.")
                        return 1
    return status


if __name__ == "__main__":
    sys.exit(main())
