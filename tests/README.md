# Orca Tests: Work in Progress

This is the beginning of Orca's new unit test and integration test support.

## Status

* Basic test coverage for the D-Bus Remote Controller: DONE
* Advanced test coverage for the D-Bus Remote Controller: TODO
  * Needed: A means to load document content, apps with UI for the navigators and presenters
* Unit test coverage of the AX* utilities: DONE
* Integration test coverage of the AX* utilities: TODO
  * Needed: Simple, but real accessible objects
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
