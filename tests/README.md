# Orca Tests: Work in Progress

This is the beginning of Orca's new unit test and integration test support.

## Status

* Basic test coverage for the D-Bus Remote Controller: DONE
* Advanced test coverage for the D-Bus Remote Controller: TODO
  * Needed: A means to load document content, apps with UI for the navigators and presenters
* Unit test coverage of the AX* utilities: DONE
* Unit test coverage of the "Managers": DONE
* Unit test coverage of the "Presenters": DONE
* Unit test coverage of the "Navigators": DONE
* Unit test coverage of generators: TODO
* Unit test coverage of scripts: TODO
* Integration/advanced test coverage of all of the above: TODO
  * Needed: Real AT-SPI2 objects
* Meson support: DONE
* Integration into Orca's Gitlab CI: TODO

## Dependencies

* [pytest](https://pytest.org)
* [pytest-mock](https://pytest-mock.readthedocs.io/) - Mock plugin for pytest

## Running Tests

### Using Meson

```bash
meson test -C _build                     # All tests
meson test -C _build --suite unit        # Unit tests only
meson test -C _build --suite integration # Integration tests only
```

### Using Pytest

```bash
pytest tests/unit_tests/                # All unit tests
coverage run -m pytest tests/unit_tests # Unit tests with coverage
python3 -m pytest tests/unit_tests/test_ax_text.py -v # Specific file
```

## Adding New Tests

### 1. Create Test File

Follow naming convention: `test_[module_name].py`

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
test_context.patch_modules({
    "orca.module1": mock_module1,
    "orca.module2": mock_module2
})
```

#### `test_context.patch_env()`

* Patches environment variables for the test duration
* Can add new variables or remove existing ones

```python
test_context.patch_env(
    {"XDG_SESSION_TYPE": "wayland", "HOME": "/tmp/test"},
    remove_vars=["DISPLAY"]
)
```

#### Shared Dependencies

Most tests should use `test_context.setup_shared_dependencies()` which provides common modules like:

* `orca.debug` - Debugging and logging
* `orca.messages` - User messages
* `orca.input_event` - Event handling
* `orca.settings` - Configuration
* `orca.keybindings` - Keyboard shortcuts
* And many others with pre-configured behaviors

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
            "mocks_config": {
                "ax_utilities_role.is_group": True,
                "has_explicit_name": True
            },
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
