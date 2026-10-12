#!/usr/bin/env bash
# Maintainer tool for periodically finding src/orca coverage gaps via the integration
# tests. It is deliberately slow -- the whole suite, run serially under coverage
# instrumentation with widened drain windows -- and is NOT how you run the tests day to
# day. To run without instrumentation, use `meson test --suite integration`.
#
# Usage: tests/integration_coverage.sh [--suite SUITE] [test_name ...]
# Defaults to the integration suite, including both browsers. Use Meson test names.
#   ORCA_BUILD_DIR          meson build directory (default: autodetect)
#   ORCA_TEST_BINARY        Orca binary to measure (default: installed build binary)
#   ORCA_TEST_TIMEOUT_SCALE multiplier for drain windows and test timeouts (default: 3)

set -uo pipefail

repo="$(git -C "$(dirname "${BASH_SOURCE[0]}")" rev-parse --show-toplevel)" || exit 1
cd "$repo" || exit 1
wrapper_rel="tests/integration_test_wrapper.py"

# coverage tracing slows Orca enough to trip the harness's drain timeouts; widen them.
export ORCA_TEST_TIMEOUT_SCALE="${ORCA_TEST_TIMEOUT_SCALE:-3}"

builddir="${ORCA_BUILD_DIR:-}"
if [ -n "$builddir" ] && [[ "$builddir" != /* ]]; then
    builddir="$repo/$builddir"
fi
if [ -z "$builddir" ]; then
    for candidate in "$repo"/_build "$repo"/_build*; do
        if [ -f "$candidate/$wrapper_rel" ]; then
            builddir="$candidate"
            break
        fi
    done
fi
if [ -z "$builddir" ] || [ ! -f "$builddir/$wrapper_rel" ]; then
    echo "No meson build dir with $wrapper_rel found; configure one or set ORCA_BUILD_DIR." >&2
    exit 1
fi

meson_args=("$@")
has_suite=false
for arg in "$@"; do
    case "$arg" in
        --suite|--suite=*) has_suite=true ;;
    esac
done
if ! "$has_suite"; then
    meson_args+=(--suite integration)
fi

rm -rf .coverage-integration htmlcov-integration
mkdir -p .coverage-integration
export COVERAGE_RCFILE="$repo/pyproject.toml"
export COVERAGE_FILE="$repo/.coverage-integration/.coverage"

ORCA_TEST_COVERAGE=1 meson test -C "$builddir" \
    --timeout-multiplier "$ORCA_TEST_TIMEOUT_SCALE" "${meson_args[@]}" \
    --num-processes 1 --print-errorlogs --logbase integration-coverage
status=$?

python3 -m coverage combine >/dev/null || status=1
python3 -m coverage html >/dev/null || status=1
echo
python3 -m coverage report || status=1
echo
echo "HTML report: $repo/htmlcov-integration/index.html"
exit "$status"
