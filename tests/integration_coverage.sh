#!/usr/bin/env bash
# Maintainer tool for periodically finding src/orca coverage gaps via the integration
# tests. It is deliberately slow -- the whole suite, run serially under coverage
# instrumentation with widened drain windows -- and is NOT how you run the tests day to
# day. To just run the integration tests, use `meson test --suite integration` (or
# `meson test` for everything).
#
# Usage: tests/integration_coverage.sh [test_file ...]   # default: all integration tests
#   ORCA_BUILD_DIR          meson build dir holding the generated wrapper (default: autodetect)
#   ORCA_TEST_BINARY        Orca binary to measure (default: orca on PATH)
#   ORCA_TEST_TIMEOUT_SCALE multiplier for the harness drain windows (default: 3)

set -uo pipefail

repo="$(git -C "$(dirname "${BASH_SOURCE[0]}")" rev-parse --show-toplevel)" || exit 1
cd "$repo" || exit 1
wrapper_rel="tests/integration_test_wrapper.py"

# coverage tracing slows Orca enough to trip the harness's drain timeouts; widen them.
export ORCA_TEST_TIMEOUT_SCALE="${ORCA_TEST_TIMEOUT_SCALE:-3}"

builddir="${ORCA_BUILD_DIR:+$repo/$ORCA_BUILD_DIR}"
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

tests=("$@")
if [ "${#tests[@]}" -eq 0 ]; then
    for f in tests/integration_tests/test_*.py; do
        # test_gsettings.py is a plain pytest in meson, not a wrapper/sandbox test.
        [ "$(basename "$f")" = "test_gsettings.py" ] && continue
        tests+=("$f")
    done
fi

rm -rf .coverage-integration htmlcov-integration
logdir=".coverage-integration/logs"
mkdir -p "$logdir"

# Each test's (very noisy) subprocess output goes to its own log; only a one-line
# result is printed, with the failing test ids surfaced when a file fails.
total="${#tests[@]}"
i=0
status=0
for test in "${tests[@]}"; do
    i=$((i + 1))
    name="$(basename "$test")"
    log="$logdir/$name.log"
    # Print the file (and progress count) before running so a long file isn't silent;
    # the result is appended to the same line when it finishes.
    printf '  [%2d/%2d] %-46s ' "$i" "$total" "$name"
    ORCA_TEST_COVERAGE=1 PYTHONPATH="$repo:$repo/src" \
        python3 "$builddir/$wrapper_rel" "$test" >"$log" 2>&1
    rc=$?
    summary="$(grep -E "in [0-9.]+s" "$log" | tail -1 | tr -d '=' | xargs)"
    if [ "$rc" -eq 0 ]; then
        printf 'ok    %s\n' "${summary:-passed}"
    elif [ "$rc" -eq 77 ]; then
        printf 'skip  %s\n' "$(grep -m1 '^SKIP:' "$log" | sed 's/^SKIP: //' | xargs)"
    else
        status=1
        printf 'FAIL  %s\n' "${summary:-see log}"
        grep -E "^FAILED " "$log" | sed 's/^/          /'
    fi
done

python3 -m coverage combine >/dev/null
python3 -m coverage html >/dev/null
echo
python3 -m coverage report
echo
echo "HTML report:   $repo/htmlcov-integration/index.html"
echo "Per-test logs: $repo/$logdir"
exit "$status"
