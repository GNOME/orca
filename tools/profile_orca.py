#!/usr/bin/python
# profile_orca.py
#
# Launches Orca under cProfile so you can interact with it normally,
# then prints the top functions when you stop it with Ctrl+C.
#
# Debug output is automatically suppressed during profiling so the
# results reflect real work, not debug overhead.
#
# Usage: python tools/profile_orca.py
#
# Copyright 2026 Igalia, S.L.
# Author: Joanmarie Diggs <jdiggs@igalia.com>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the
# Free Software Foundation, Inc., Franklin Street, Fifth Floor,
# Boston MA  02110-1301 USA.

"""Profiles a running Orca session under cProfile."""

# pylint: disable=too-many-locals

from __future__ import annotations

import cProfile
import os
import pstats
import runpy
import shutil
import sys

_TOP_N = 40
_CALLERS_N = 10
_CALLERS_FOR = 10
_CALLEES_FOR = 5


def _short_path(filename: str) -> str:
    """Shortens a path to the orca-relative portion."""

    if "/orca/" in filename:
        return "orca/" + filename.split("/orca/", 1)[1]
    return filename


def _format_key(key: tuple[str, int, str]) -> str:
    """Formats a (filename, line, function) tuple."""

    return f"{_short_path(key[0])}:{key[1]}({key[2]})"


def _print_orca_stats(all_stats: dict) -> None:
    """Prints the top orca functions by total time."""

    sorted_keys = [key for key in all_stats if "/orca/" in key[0]]
    sorted_keys.sort(key=lambda k: all_stats[k][2], reverse=True)

    print(
        f"{'ncalls':>16s}   {'tottime':>8s}   {'cumtime':>8s}"
        f"   {'percall':>8s}   filename:lineno(function)"
    )
    for key in sorted_keys[:_TOP_N]:
        cc, nc, tt, ct, _callers = all_stats[key]
        calls_str = str(nc) if cc == nc else f"{nc}/{cc}"
        per_call = tt / nc if nc else 0
        if per_call >= 0.001:
            per_call_str = f"{per_call:.3f}s"
        else:
            per_call_str = f"{per_call * 1e6:.0f}µs"
        print(
            f"{calls_str:>16s}   {tt:>8.3f}   {ct:>8.3f}   {per_call_str:>8s}   {_format_key(key)}"
        )


def _print_callers(all_stats: dict) -> None:
    """Prints the top callers for the most expensive functions."""

    sorted_keys = [key for key in all_stats if "/orca/" in key[0]]
    sorted_keys.sort(key=lambda k: all_stats[k][2], reverse=True)

    for key in sorted_keys[:_CALLERS_FOR]:
        _cc, nc, _tt, _ct, callers = all_stats[key]
        if not callers:
            continue

        print(f"\n  Callers of {_format_key(key)} (called {nc} times):")
        print(f"  {'ncalls':>12s}   caller")

        caller_list = []
        for caller_key, caller_data in callers.items():
            nc = caller_data[0]
            caller_list.append((nc, caller_key))
        caller_list.sort(reverse=True)

        for nc, caller_key in caller_list[:_CALLERS_N]:
            print(f"  {nc:>12d}   {_format_key(caller_key)}")


def _print_callees(all_stats: dict) -> None:
    """Prints the top callees for the functions with the highest cumulative time."""

    sorted_keys = [key for key in all_stats if "/orca/" in key[0]]
    sorted_keys.sort(key=lambda k: all_stats[k][3], reverse=True)

    callees: dict[tuple, list[tuple[int, float, tuple]]] = {}
    for callee_key, (_cc, _nc, _tt, _ct, callers) in all_stats.items():
        for caller_key, caller_data in callers.items():
            nc, _nrec, _callee_tt, callee_ct = caller_data
            callees.setdefault(caller_key, []).append((nc, callee_ct, callee_key))

    for key in sorted_keys[:_CALLEES_FOR]:
        key_callees = callees.get(key, [])
        if not key_callees:
            continue

        key_callees.sort(key=lambda x: x[1], reverse=True)

        _cc, _nc, _tt, ct, _callers = all_stats[key]
        print(f"\n  Callees of {_format_key(key)} (cumtime {ct:.3f}):")
        print(f"  {'ncalls':>12s}   {'cumtime':>8s}   callee")

        for nc, callee_ct, callee_key in key_callees[:_CALLERS_N]:
            print(f"  {nc:>12d}   {callee_ct:>8.3f}   {_format_key(callee_key)}")


def _build_callees_map(all_stats: dict) -> dict[tuple, list[tuple[int, float, tuple]]]:
    """Builds a map of caller -> [(ncalls, cumtime, callee_key), ...]."""

    callees: dict[tuple, list[tuple[int, float, tuple]]] = {}
    for callee_key, (_cc, _nc, _tt, _ct, callers) in all_stats.items():
        for caller_key, caller_data in callers.items():
            nc, _nrec, _callee_tt, callee_ct = caller_data
            callees.setdefault(caller_key, []).append((nc, callee_ct, callee_key))
    return callees


def _find_key(all_stats: dict, name: str) -> tuple | None:
    """Finds a stats key matching the given function name."""

    matches = [key for key in all_stats if key[2] == name and "/orca/" in key[0]]
    if not matches:
        return None
    matches.sort(key=lambda k: all_stats[k][3], reverse=True)
    return matches[0]


def _print_target(all_stats: dict, name: str, depth: int) -> None:
    """Prints a breakdown of where time is spent inside a function."""

    key = _find_key(all_stats, name)
    if key is None:
        print(f"Function '{name}' not found in profile data.", file=sys.stderr)
        return

    callees_map = _build_callees_map(all_stats)

    _cc, nc, tt, ct, _callers = all_stats[key]
    print(f"\n  {_format_key(key)}")
    print(f"  calls: {nc}   tottime: {tt:.3f}   cumtime: {ct:.3f}")

    direct = sorted(callees_map.get(key, []), key=lambda x: x[1], reverse=True)
    print(f"\n  {'ncalls':>10s}   {'cumtime':>8s}   {'percall':>8s}   callee")
    for d_nc, d_ct, d_key in direct[:_TOP_N]:
        if d_ct < 0.001:
            break
        per_call = d_ct / d_nc if d_nc else 0
        if per_call >= 0.001:
            per_call_str = f"{per_call:.3f}s"
        else:
            per_call_str = f"{per_call * 1e6:.0f}µs"
        print(f"  {d_nc:>10d}   {d_ct:>8.3f}   {per_call_str:>8s}   {_format_key(d_key)}")

    if depth > 0:
        print(f"\n  Callee tree (depth {depth}, top {_CALLERS_N} per level):")
        print(f"  {'ncalls':>10s}   {'cumtime':>8s}   {'percall':>8s}   callee")
        _print_target_tree(callees_map, key, depth, indent=2)

    print("\n  Tip: use --target <callee_name> to drill into any function above.")


def _print_target_tree(
    callees_map: dict,
    key: tuple,
    depth: int,
    indent: int,
) -> None:
    """Prints the callee tree, limited to top N per level."""

    key_callees = callees_map.get(key, [])
    if not key_callees:
        return

    key_callees = sorted(key_callees, key=lambda x: x[1], reverse=True)
    tree_prefix = " " * indent

    for shown, (nc, callee_ct, callee_key) in enumerate(key_callees):
        if callee_ct < 0.001 or shown >= _CALLERS_N:
            break
        per_call = callee_ct / nc if nc else 0
        if per_call >= 0.001:
            per_call_str = f"{per_call:.3f}s"
        else:
            per_call_str = f"{per_call * 1e6:.0f}µs"
        callee_str = _format_key(callee_key)
        print(f"  {nc:>10d}   {callee_ct:>8.3f}   {per_call_str:>8s}   {tree_prefix}{callee_str}")
        if depth > 1:
            _print_target_tree(callees_map, callee_key, depth - 1, indent + 4)


def main() -> None:
    """Launches Orca under cProfile and prints the results."""

    import argparse

    parser = argparse.ArgumentParser(description="Profile a running Orca session.")
    parser.add_argument(
        "--target",
        metavar="FUNCTION",
        help="Show detailed breakdown for the named function.",
    )
    parser.add_argument(
        "--depth",
        type=int,
        default=0,
        help="Callee tree depth for --target (default: 0, summary only).",
    )
    args = parser.parse_args()

    orca_bin = shutil.which("orca")
    if orca_bin is None:
        print("orca not found in PATH.", file=sys.stderr)
        sys.exit(1)

    print("Launching Orca under cProfile (debug output suppressed).")
    print("Interact with Orca normally, then Ctrl+C when done.\n")

    os.environ["ORCA_PROFILING"] = "1"

    sys.argv = [orca_bin, "--replace"]

    profiler = cProfile.Profile()
    profiler.enable()
    try:
        runpy.run_path(orca_bin, run_name="__main__")
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        profiler.disable()

    all_stats: dict = pstats.Stats(profiler).stats  # type: ignore[attr-defined]

    if args.target:
        print(f"\n{'=' * 72}")
        print(f"Focus: {args.target} (depth {args.depth})")
        print(f"{'=' * 72}")
        _print_target(all_stats, args.target, args.depth)
    else:
        print(f"\n{'=' * 72}")
        print(f"Top {_TOP_N} functions by total time (orca only)")
        print(f"{'=' * 72}\n")
        _print_orca_stats(all_stats)

        print(f"\n{'=' * 72}")
        print(f"Top callers for the {_CALLERS_FOR} most expensive functions")
        print(f"{'=' * 72}")
        _print_callers(all_stats)

        print(f"\n{'=' * 72}")
        print(f"Top callees for the {_CALLEES_FOR} functions with highest cumulative time")
        print(f"{'=' * 72}")
        _print_callees(all_stats)


if __name__ == "__main__":
    main()
