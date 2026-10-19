# Orca Tests

## Dependencies

The unit tests need:

* [pytest](https://pytest.org)
* [pytest-mock](https://pytest-mock.readthedocs.io/) - Mock plugin for pytest

The integration tests additionally need the following, on top of what Orca itself requires.
Some missing dependencies cause skips; others cause import or setup failures. Tests which
launch Orca need an installed build of the version being tested.

* Xvfb
* `dbus-run-session`, `gdbus`, and `dbus-update-activation-environment`
* AT-SPI's `at-spi-bus-launcher` and `at-spi2-registryd`
* `pgrep` (from procps) and `fusermount` (for sandbox FUSE cleanup)
* Python GObject introspection and Cairo bindings, with the AT-SPI, GTK3, and PangoCairo typelibs
* `glib-compile-schemas` for the GSettings tests
* `notification-daemon` and `notify-send` (from libnotify) for the notification tests.
* The DejaVu Serif, DejaVu Sans, and DejaVu Sans Mono fonts for consistent line wrapping
* VTE 2.91 (GTK3), including its typelib, Python curses, xterm terminfo, bash, less, nano, vim,
  and `seq` (from coreutils), for the terminal tests
* liblouis's Python bindings and en-us-g1/en-us-g2 tables for the braille tests. Its pkg-config
  metadata must be available when building Orca so it can locate the tables (in Fedora and
  openSUSE, install `liblouis-devel`).
* MathCAT enabled in the installed Orca build for the math tests.
* Chrome (beta preferred) or Chromium for the web tests.
* Firefox (Nightly preferred) for the Firefox tests.
* Atril for PDF navigation and selection tests. Tests that depend
  on its selection fixes require 1.28.7 or later.
* `python-xlib` for window setup when running tests with Firefox or Atril.

## Running Tests

### Using Pytest

```bash
pytest tests/unit_tests/                # All unit tests
coverage run -m pytest tests/unit_tests # Unit tests with coverage
python3 -m pytest tests/unit_tests/test_ax_text.py -v # Specific file
```

### Using Meson

Orca's tests are grouped into the following named suites:

* "unit": the only suite run by default with `meson test`
* "integration": the superset of the following:
    * "core": infrastructure such as GSettings, D-Bus support, and browser smoke tests
    * "document": document viewers and editors (currently Atril)
    * "gtk3": non-terminal GTK3 UI tests
    * "gtk3-terminal": for terminal applications using VTE for GTK3
    * "chromium": for web content using Chrome (beta preferred) or Chromium
    * "gecko": for web content using Firefox (Nightly preferred)

Note that coverage for GTK4 and Qt, along with additional applications, is in
progress.

```bash
meson test -C _build
meson test -C _build --suite <suite name>
```

Downstream distributions may wish to run the small `core` suite to check basic
environment readiness. Failures in this suite can identify a dependency or
accessibility configuration problem that may need to be addressed downstream.
Such issues should be investigated before concluding the failure is a bug in Orca
or in its test harness.

For example, browser accessibility may require `ACCESSIBILITY_ENABLED=1` (Chromium)
or `GNOME_ACCESSIBILITY=1` (Firefox) for the browser to show up in the AT-SPI
application registry. If AT-SPI doesn't know an application exists, Orca cannot
provide access to it. For this reason, the `core` suite's browser smoke tests
include coverage for the browser being launched without the variables set in
the environment to help identify this need.

The other integration-test suites are mainly intended for maintainer use for the
purpose of preventing regressions in Orca. Documenting all expected dependencies
and versions and ensuring compatibility with additional distros are still pending.
At the present time Fedora and openSUSE are officially supported. If all of the
integration tests pass (modulo flakes) on a distro not listed as supported, please
let us know so that we can add it to a "known to work on" list.

The integration tests cannot run while Orca is already active on the user's
session because each test launches and drives its own Orca. It was decided
that the test harness should not first kill any running instance of Orca
because doing so might be unexpected. If you rely on Orca in your active
session, you can still run the tests by signing in as a second local user
(via `su` or `ssh`) and running them from there.

Most integration tests cover user interactions with applications and toolkits
by simulating keystrokes, waiting for Orca's response, and checking the resulting
speech and braille output. Running these tests therefore takes a fair amount of
time. There are currently over 275 Meson test runs containing over 1,500 test
cases, many involving numerous simulated keystrokes. CI divides the suites into
separate container jobs that can run in parallel. Local runs do not require
containers, and application tests run sequentially by default. A full local run
can take around 90 minutes, depending on the machine and installed applications.

Running tests directly on the local system is supported and tests the installed
applications and toolkits. Supporting containers for local runs would add setup
and maintenance requirements, along with resource management and validation for
parallel runs. CI already provides container-based testing, so dedicated support
for local containers is not currently planned.

`ORCA_TEST_USER_AGENT_PATH` overrides the browser executable. It must match the
selected suite; this is not checked by the harness. For example:

```bash
ORCA_TEST_USER_AGENT_PATH=/usr/bin/firefox meson test -C _build --suite gecko
ORCA_TEST_USER_AGENT_PATH=/opt/google/chrome-canary/chrome meson test -C _build --suite chromium
```

## Adding New Integration Tests

Prefer integration tests for new coverage. They exercise Orca with real
applications and verify the speech and braille output associated with both
native navigation and Orca commands.

### 1. Choose a Test File and Content

Look for a related test in `tests/integration_tests/` and extend it when
practical. Otherwise, create a file named `test_[feature].py`, following
similar existing tests.

Reuse the existing test applications in `tests/integration_tests/apps/`
and fixtures in `tests/integration_tests/orca_fixtures.py` when practical.
Web pages live in `tests/integration_tests/web_pages/`, and test documents
live in `tests/integration_tests/documents/`.

### 2. Test the User's Experience

Simulate the user's key presses using the functions in
`tests/integration_tests/harness/keyboard.py`, such as `tap_key()` and
`press_chord()`, and check the resulting speech and braille. Existing
tests provide plenty of examples of native navigation and Orca commands.

Include relevant variations, such as navigating both forward and backward.
For bug fixes, confirm that the test fails without the fix and passes
with it.

### 3. Register New Files with Meson

Add each new test file to the appropriate group in `orca_integration_tests`
in `tests/meson.build`. Files in the `web` group run in both Chromium and
Firefox.

Adding tests to an already registered file requires no Meson changes.

### 4. Run the Tests

Build and install the version of Orca being tested, then run the affected
tests with Meson. For example:

    meson test -C _build --suite gtk3 test_caret_navigation
    meson test -C _build --suite chromium test_web_code_block
    meson test -C _build --suite gecko test_web_code_block_gecko

Run web tests in both browsers. See "Running Tests" above for the other
suites and requirements.

## Adding New Unit Tests

Integration tests are preferred. Add unit tests only for behavior that
cannot be adequately tested through integration tests.

### 1. Create Test File

Follow naming convention: `test_[module_name].py`

Add each new file to the `unit_tests` list in `tests/meson.build`.

### 2. Test File Structure

```python
from typing import TYPE_CHECKING
import pytest

if TYPE_CHECKING:
    from .orca_test_context import OrcaTestContext
    from unittest.mock import MagicMock


@pytest.mark.unit
class TestMyModule:
    """Test MyModule class methods."""

    def _setup_dependencies(self, test_context: OrcaTestContext) -> dict[str, MagicMock]:
        """Set up mocks for my_module dependencies."""

        # Use setup_shared_dependencies for common modules
        additional_modules = ["orca.module_specific_to_my_module"]
        essential_modules = test_context.setup_shared_dependencies(additional_modules)

        # Configure module-specific behavior
        my_mock = essential_modules["orca.module_specific_to_my_module"]
        my_mock.some_method.return_value = "expected_value"

        return essential_modules

    def test_my_function(self, test_context: OrcaTestContext) -> None:
        """Test MyModule.my_function behavior."""

        # Set up mocks BEFORE importing the module under test.
        # Python's import system caches modules - if MyModule imports its
        # dependencies before we mock them, it gets the real modules.
        self._setup_dependencies(test_context)

        # Import AFTER mocks are set up so MyModule gets our mocked dependencies.
        from orca.my_module import MyModule

        result = MyModule.my_function()
        assert result == "expected_value"
```

### 3. Mocking and Patching

The `test_context` fixture provides testing utilities using pytest-mock patterns:

#### `test_context.Mock()`

* Creates mock objects consistently across all tests
* Use `spec=` when the class itself hasn't been replaced (even if you're mocking instances of it)
* Omit `spec=` for method replacements, function replacements, class replacements, and ad-hoc test data

```python
# Use spec when the class itself hasn't been replaced
mock_accessible = test_context.Mock(spec=Atspi.Accessible)
mock_accessible.get_name.return_value = "Test Button"

# Mock a function and use the spec mock as return value
mock_match_rule_new = test_context.Mock()
test_context.patch("gi.repository.Atspi.MatchRule.new", side_effect=mock_match_rule_new)
mock_rule = test_context.Mock(spec=Atspi.MatchRule)
mock_match_rule_new.return_value = mock_rule

# Don't use spec when the class itself is being mocked
mock_state_set_class = test_context.Mock()
test_context.patch("gi.repository.Atspi.StateSet", new=mock_state_set_class)
mock_state_set = test_context.Mock()  # StateSet class was replaced, can't use spec
mock_state_set_class.return_value = mock_state_set

# Don't use spec for method/function replacements
debug_mock.print_message = test_context.Mock()
mock_function = test_context.Mock()
test_context.patch("module.function", side_effect=mock_function)

# Don't use spec for ad-hoc test data
test_config = test_context.Mock()
test_config.enabled = True
```

#### `test_context.patch()` and `test_context.patch_object()`

* Returns mock objects for assertions
* Use `patch()` for string-based patching of deep module paths
* Use `patch_object()` for patching attributes on existing objects

```python
mock_clear_cache = test_context.patch("gi.repository.Atspi.Accessible.clear_cache")
AXObject.clear_cache(mock_accessible, recursive=True)
mock_clear_cache.assert_called_once_with(mock_accessible)

mock_present_line = test_context.patch_object(presenter, "present_line")
presenter.go_previous_line(script_mock, event_mock)
mock_present_line.assert_called_once_with(script_mock, event_mock)
```

#### `test_context.patch_module()` and `test_context.patch_modules()`

* Use instead of `patch()` or `patch_object()` when you need to replace entire modules in `sys.modules`
* Useful when the module under test imports dependencies at module level
* Ensures the mock module is available when the test module imports it

```python
# Single module replacement
mock_module = test_context.Mock()
test_context.patch_module("orca.special_module", mock_module)

# Multiple modules at once
test_context.patch_modules({"orca.module1": mock_module1, "orca.module2": mock_module2})
```

#### `test_context.patch_env()`

* Patches environment variables for the test duration
* Can add new variables or remove existing ones

```python
test_context.patch_env(
    {"XDG_SESSION_TYPE": "wayland", "HOME": "/tmp/test"}, remove_vars=["DISPLAY"]
)
```

#### Shared Dependencies

Most tests should use `test_context.setup_shared_dependencies()` which provides
common modules.

### 4. Parameterized Tests

Use pytest's parameterize decorator for testing multiple inputs efficiently.

#### Simple Parameters

For straightforward test cases:

```python
@pytest.mark.parametrize(
    "focus, window, expected",
    [
        pytest.param(None, None, True, id="both_none"),
        pytest.param(None, "window", False, id="focus_none_window_set"),
        pytest.param("focus", None, False, id="focus_set_window_none"),
        pytest.param("focus", "window", False, id="both_set"),
    ],
)
def test_focus_and_window_are_unknown(self, test_context, focus, window, expected):
    """Test FocusManager.focus_and_window_are_unknown."""

    self._setup_dependencies(test_context)
    from orca.focus_manager import FocusManager

    manager = FocusManager()
    focus_obj = test_context.Mock(spec=Atspi.Accessible) if focus else None
    window_obj = test_context.Mock(spec=Atspi.Accessible) if window else None
    test_context.patch_object(manager, "_focus", new=focus_obj)
    test_context.patch_object(manager, "_window", new=window_obj)
    result = manager.focus_and_window_are_unknown()
    assert result == expected
```

#### Dictionary with ID Lambda

For tests with complex configurations:

```python
@pytest.mark.parametrize(
    "case",
    [
        {
            "id": "layout_only_role",
            "mocks_config": {"ax_object.get_role": Atspi.Role.FILLER},
            "expected": True,
        },
        {
            "id": "group_with_explicit_name",
            "mocks_config": {"ax_utilities_role.is_group": True, "has_explicit_name": True},
            "expected": False,
        },
        {
            "id": "layered_pane_in_desktop",
            "mocks_config": {
                "ax_utilities_role.is_layered_pane": True,
                "ax_utilities_role.is_desktop_frame": True,
                "ax_object.find_ancestor": "desktop",
            },
            "expected": True,
        },
    ],
    ids=lambda case: case["id"],
)
def test_is_layout_only_scenarios(self, test_context: OrcaTestContext, case: dict):
    """Test AXUtilities.is_layout_only with various scenarios."""

    mocks_config = case["mocks_config"]
    expected = case["expected"]
    essential_modules = self._setup_dependencies(test_context)

    for mock_path, mock_value in mocks_config.items():
        if mock_path == "has_explicit_name":
            test_context.patch(
                "orca.ax_utilities.AXUtilities.has_explicit_name",
                return_value=mock_value,
            )
        elif mock_path.startswith("ax_object.get_role"):
            essential_modules["orca.ax_object"].AXObject.get_role = test_context.Mock(
                return_value=mock_value
            )
        elif mock_path.startswith("ax_utilities_role."):
            method_name = mock_path.split(".", 1)[1]
            setattr(
                essential_modules["orca.ax_utilities_role"].AXUtilitiesRole,
                method_name,
                test_context.Mock(return_value=mock_value),
            )

    from orca.ax_utilities import AXUtilities

    mock_obj = test_context.Mock(spec=Atspi.Accessible)
    result = AXUtilities.is_layout_only(mock_obj)
    assert result is expected
```

Benefits of parameterized tests:

* Test multiple scenarios efficiently
* Clear test case identification
* Easy to add new test cases
* Better coverage with less code duplication
* Dictionary pattern keeps related test data together
