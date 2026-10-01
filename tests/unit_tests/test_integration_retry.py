"""Checks retry decisions using real pytest subprocesses and fixtures."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

_RUNNER = Path(__file__).parents[1] / "integration_retry.py"


def _run(tmp_path: Path, source: str, *, retry: bool = True) -> subprocess.CompletedProcess:
    test_file = tmp_path / "test_example.py"
    test_file.write_text(source, encoding="utf-8")
    env = os.environ.copy()
    env.pop("PYTEST_ADDOPTS", None)
    env.pop("ORCA_TEST_RETRY_DIR", None)
    env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
    if retry:
        env["ORCA_TEST_RETRY_DIR"] = str(tmp_path / "logs")
    build = tmp_path / "build"
    build.mkdir()
    return subprocess.run(
        [sys.executable, str(_RUNNER), str(test_file)],
        cwd=build,
        env=env,
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )


def test_retry_uses_fresh_fixtures_and_only_failed_cases(tmp_path: Path) -> None:
    """A recovered assertion does not rerun passing or other parametrized cases."""

    result = _run(
        tmp_path,
        """
import os
from pathlib import Path
import pytest
root = Path(__file__).parent

@pytest.mark.xfail(strict=True)
def test_known_failure():
    assert False

@pytest.fixture(scope="session", autouse=True)
def application():
    with (root / "fixtures").open("a") as log:
        log.write(f"setup {os.getpid()}\\n")
    yield
    with (root / "fixtures").open("a") as log:
        log.write(f"teardown {os.getpid()}\\n")

@pytest.mark.parametrize("value", ["passes", "fails.once"])
def test_example(value):
    marker = root / value
    previous = marker.exists()
    with marker.open("a") as log:
        log.write("called\\n")
    if value == "fails.once":
        assert previous, "original assertion"
""",
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert (tmp_path / "passes").read_text() == "called\n"
    assert (tmp_path / "fails.once").read_text() == "called\ncalled\n"
    setup1, teardown1, setup2, teardown2 = (tmp_path / "fixtures").read_text().splitlines()
    assert setup1.split()[1] == teardown1.split()[1]
    assert setup2.split()[1] == teardown2.split()[1]
    assert setup1 != setup2
    assert "original assertion" in (tmp_path / "logs/test_example.first.log").read_text()
    summary = (tmp_path / "logs/test_example.summary").read_text()
    assert summary == "PASSED ON RETRY: test_example.py::test_example[fails.once]\n"


@pytest.mark.parametrize("second", ["assert False", "pytest.skip('unavailable')"])
def test_retry_must_pass(tmp_path: Path, second: str) -> None:
    """A second failure or skip cannot turn the first failure into a pass."""

    result = _run(
        tmp_path,
        f"""
from pathlib import Path
import pytest
marker = Path(__file__).with_suffix(".attempts")
def test_example():
    previous = marker.exists()
    with marker.open("a") as log:
        log.write("called\\n")
    if previous:
        {second}
    assert False
""",
    )
    assert result.returncode == 1, result.stdout + result.stderr
    assert (tmp_path / "test_example.attempts").read_text() == "called\ncalled\n"
    assert "FAILED ON RETRY" in result.stdout


@pytest.mark.parametrize(
    "source",
    [
        "def test_example():\n    raise RuntimeError('broken infrastructure')\n",
        (
            "import pytest\n@pytest.fixture\ndef broken():\n    assert False\n"
            "def test_example(broken):\n    pass\n"
        ),
        (
            "import pytest\n@pytest.fixture\ndef broken():\n    yield\n    assert False\n"
            "def test_example(broken):\n    assert False\n"
        ),
        "import pytest\n@pytest.mark.xfail(strict=True)\ndef test_example():\n    pass\n",
        "import os\ndef test_example():\n    os._exit(1)\n",
        "import os\ndef test_example():\n    os._exit(0)\n",
        "def test_example(:\n",
    ],
)
def test_errors_are_not_retried(tmp_path: Path, source: str) -> None:
    """Setup, teardown, collection, process errors and strict XPASS remain failures."""

    result = _run(tmp_path, source)
    assert result.returncode != 0, result.stdout + result.stderr
    assert not (tmp_path / "logs/test_example.retry.log").exists()
    assert not (tmp_path / "logs/test_example.summary").exists()


@pytest.mark.parametrize(
    "source",
    [
        "def test_example():\n    pass\n",
        "import pytest\n@pytest.mark.xfail(strict=True)\ndef test_example():\n    assert False\n",
    ],
)
def test_success_and_expected_failure_are_not_retried(tmp_path: Path, source: str) -> None:
    """Passing and expected-failure results keep their normal pytest semantics."""

    result = _run(tmp_path, source)
    assert result.returncode == 0, result.stdout + result.stderr
    assert not list((tmp_path / "logs").iterdir())


def test_local_failure_is_not_retried(tmp_path: Path) -> None:
    """Local runs keep the original failure without enabling the CI retry."""

    result = _run(tmp_path, "def test_example():\n    assert False\n", retry=False)
    assert result.returncode == 1
    assert "1 failed" in result.stdout
    assert not (tmp_path / "logs").exists()
