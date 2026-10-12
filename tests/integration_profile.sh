#!/usr/bin/env bash
# Runs the integration tests under cProfile and merges the per-process results.
#
# Usage: tests/integration_profile.sh [--suite SUITE] [test_name ...]
# Defaults to the integration suite, including both browsers. Use Meson test names.
#   ORCA_BUILD_DIR          meson build directory (default: autodetect)
#   ORCA_TEST_BINARY        Orca binary to measure (default: installed build binary)
#   ORCA_TEST_TIMEOUT_SCALE multiplier for drain windows and test timeouts (default: 3)

set -uo pipefail

repo="$(git -C "$(dirname "${BASH_SOURCE[0]}")" rev-parse --show-toplevel)" || exit 1
cd "$repo" || exit 1
wrapper_rel="tests/integration_test_wrapper.py"

# Tracing slows Orca enough to trip timing-sensitive tests, so widen the drain windows.
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

profiledir="$repo/.profile-integration"
rm -rf "$profiledir"
mkdir -p "$profiledir"
export ORCA_TEST_PROFILE="$profiledir"

meson test -C "$builddir" \
    --timeout-multiplier "$ORCA_TEST_TIMEOUT_SCALE" "${meson_args[@]}" \
    --num-processes 1 --print-errorlogs --logbase integration-profile
status=$?

echo
python3 "$repo/tools/profile_orca.py" --load "$profiledir" || status=1
echo
echo "Per-process data: $profiledir/profile-*.pstats"
echo "Narrow further:   tools/profile_orca.py --load $profiledir --module ax_object"
echo "                  tools/profile_orca.py --load $profiledir --target find_ancestor --depth 2"
exit "$status"
