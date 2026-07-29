#!/usr/bin/env bash
# Runs the integration tests under cProfile and merges the per-process results.
#
# Usage: tests/integration_profile.sh [test_file ...]   # default: all
#   ORCA_BUILD_DIR          meson build dir holding the generated wrapper (default: autodetect)
#   ORCA_TEST_BINARY        Orca binary to measure (default: orca on PATH)
#   ORCA_TEST_TIMEOUT_SCALE multiplier for the harness drain windows (default: 3)

set -uo pipefail

repo="$(git -C "$(dirname "${BASH_SOURCE[0]}")" rev-parse --show-toplevel)" || exit 1
cd "$repo" || exit 1
wrapper_rel="tests/integration_test_wrapper.py"

# Tracing slows Orca enough to trip timing-sensitive tests, so widen the drain windows.
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

profiledir="$repo/.profile-integration"
logdir="$profiledir/logs"
rm -rf "$profiledir"
mkdir -p "$logdir"
export ORCA_TEST_PROFILE="$profiledir"

total="${#tests[@]}"
i=0
status=0
for test in "${tests[@]}"; do
    i=$((i + 1))
    name="$(basename "$test")"
    log="$logdir/$name.log"
    printf '  [%2d/%2d] %-46s ' "$i" "$total" "$name"
    PYTHONPATH="$repo:$repo/src" \
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

echo
python3 "$repo/tools/profile_orca.py" --load "$profiledir"
echo
echo "Per-process data: $profiledir/profile-*.pstats"
echo "Per-test logs:    $logdir"
echo "Narrow further:   tools/profile_orca.py --load $profiledir --module ax_object"
echo "                  tools/profile_orca.py --load $profiledir --target find_ancestor --depth 2"
exit "$status"
