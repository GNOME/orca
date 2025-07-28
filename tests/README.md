# Orca Tests: Work in Progress

This is the beginning of Orca's new unit test and integration test support.

## Status

* Basic test coverage for the D-Bus Remote Controller: DONE
* Advanced test coverage for the D-Bus Remote Controller: TODO
  * Needed: A means to load document content, apps with UI for the navigators and presenters
* Unit test coverage of the AX* utilities: DONE
* Integration test coverage of the AX* utilities: TODO
  * Needed: Simple, but real accessible objects
* Unit test coverage of the "Managers": IN PROGRESS
* Unit test coverage of the "Presenters" and generators: TODO
* Unit test coverage of scripts: TODO
* Meson support: DONE
* Integration into Orca's Gitlab CI: TODO

## Dependencies

* [pytest](https://pytest.org)

## Running Tests

### Using Meson (Recommended)

```bash
# Run all tests
meson test -C _build

# Run only unit tests
meson test -C _build --suite unit

# Run only integration tests (requires Orca to be running)
meson test -C _build --suite integration
```

### Using pytest directly

#### Options

* `-v` - Verbose output showing individual test names
* `-s` - Show print statements and diagnostics
* `-m "marker"` - Run tests with specific markers

#### Unit Tests

```bash
pytest tests/unit_tests/           # All unit tests
pytest tests/ -m "unit"            # Unit tests across all directories
```

#### Integration Tests (Orca must be running)

```bash
pytest tests/integration_tests/    # All integration tests
pytest tests/ -m "dbus"            # D-Bus specific integration tests
```

## Test Configuration

Each test directory has a `conftest.py` file containing shared fixtures:

* **`tests/unit_tests/conftest.py`**: Mock fixtures for isolated testing
* **`tests/integration_tests/conftest.py`**: Real service fixtures and timeouts

## Writing Unit Tests: Mocking

Mocking is the practice of replacing dependencies -- like other modules, classes, or functions -- with
controlled, predictable objects. This makes it possible to test the specific code of interest without
failures arising due to related or dependent code.

There are three main techniques used in this project, each for a different purpose.

### 1. The Main Fixture: `mock_orca_dependencies`

For most tests, you will only need the `mock_orca_dependencies` fixture, which is defined in `tests/unit_tests/conftest.py`.

* **What it does:** This fixture automatically mocks a large set of commonly used Orca modules
  (`orca.debug`, `orca.ax_object`, `orca.settings`, etc.), replacing them with`unittest.mock.Mock`
    objects.
* **How to use it:** Simply add it as an argument to your test function. You can then access the
   mocks as attributes of the fixture.

    ```python
    def test_my_function(mock_orca_dependencies):
        # The 'orca.debug' module is now a mock. We can check if it was called.
        mock_orca_dependencies.debug.print_message.assert_called()
    ```

### 2. Targeted Mocking: `monkeypatch`

When you need to change the behavior of a function or attribute for a *specific test case*, use the
`monkeypatch` fixture provided by pytest.

* **What it does:** `monkeypatch.setattr()` lets you temporarily replace a function, method, or
  attribute on any class or module. The change is automatically undone after the test completes.
* **How to use it:** Use it *inside your test* to control the return value of a function or to
   simulate an error.

    ```python
    def test_get_size_handles_error(self, mock_accessible, monkeypatch, mock_orca_dependencies):
        # Make Atspi.Component.get_size raise an error for this test only.
        def raise_glib_error(obj, coord_type):
            raise GLib.GError("Size error")
        monkeypatch.setattr(Atspi.Component, "get_size", raise_glib_error)

        # Now call Orca's wrapper function that we expect to handle the Atspi error.
        result = AXComponent.get_size(mock_accessible)
        assert result == (-1, -1)
    ```

### 3. Module-Level Mocking: `sys.modules` and `clean_module_cache()`

This is the most complex technique and is used when we need to mock a module *before* the code being
tested imports it.

* **What it does:** Python caches imported modules in `sys.modules`. By directly modifying this
   dictionary (usually with `patch.dict` inside a fixture), we can replace an entire module (like
   `gi` or `dasbus`) with a mock *before any of our code runs*.
* **The 'wrong module' problem:** If you mock a dependency (e.g., `orca.ax_object`) and then import
   the module that uses it (e.g., `from orca.ax_component import AXComponent`), Python might use a
   cached, *un-mocked* version of `orca.ax_component`. As a result, we have `clean_module_cache()`,
   a utility which forces Python to re-import the module, ensuring it sees our mocks.
* **How to use it:** This pattern is common in fixtures that set up complex environments, like
    `mock_dbus_service`.

    ```python
    # Inside a fixture in conftest.py
    with patch.dict(sys.modules, {"gi": mock_gi, "dasbus": mock_dasbus}):
        # Because we mocked 'gi' and 'dasbus', the following import will cause the mocks to be used
        # instead of the actual libraries.
        from orca import dbus_service
        yield dbus_service

    # Inside a test file
    def test_my_component(self, monkeypatch, mock_orca_dependencies):
        # We need to change a dependency of ax_component before importing it.
        monkeypatch.setattr(mock_orca_dependencies.ax_object, "supports_component", lambda obj: False)

        # Clean the cache so the next import is fresh.
        clean_module_cache("orca.ax_component")
        from orca.ax_component import AXComponent # This now sees our monkeypatched function.

        # ... rest of the test ...
    ```

### Summary: Which Mocking Tool to Use?

* **Creating a new test?** Add `mock_orca_dependencies` to your test function.
* **Need to test a specific return value or error?** Use `monkeypatch.setattr()` inside your test.
* **Testing a module that needs its dependencies mocked *before* it runs?** Use a fixture with
  `patch.dict(sys.modules, ...)` and remember to call `clean_module_cache()` in your test before
  importing the module you're testing.

## Troubleshooting Mock-Related Test Failures

When you've written correct code but tests fail due to mocking issues:

### "Argument 0 does not allow None as a value" with Valid Code

**Problem:** Your code properly checks for `None` but still crashes on GObject methods.
**Root cause:** `AXObject.is_valid` is mocked to always return `True`, breaking null-checking.

```python
# Bad mock - breaks null checking
AXObject.is_valid = Mock(return_value=True)  # Always True, even for None!

# Good mock - preserves null checking
AXObject.is_valid = Mock(side_effect=lambda obj: obj is not None)
```

### "expected GObject but got <Mock...>"

**Problem:** Your code gets a Mock object where it expects a real GObject.
**Solution:** Mock the functions that interact with GObjects, not the objects themselves:

```python
# Add these mocks to handle functions that can't work with Mock objects
AXTable.get_cell_coordinates = Mock(return_value=(-1, -1))
AXText.get_caret_offset = Mock(return_value=-1)
AXText.update_cached_selected_text = Mock()
```

### Finding Mock Issues

1. **Check fixture mocks:** Look in `conftest.py` for overly broad mocks (like `return_value=True`)
2. **Test with real values:** Temporarily remove mocks to see if your code actually works
3. **Mock smarter:** Use `side_effect` to preserve the original function's logic for edge cases
