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
        _cc, _nc, _tt, _ct, callers = all_stats[key]
        if not callers:
            continue

        print(f"\n  Callers of {_format_key(key)}:")
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


def main() -> None:
    """Launches Orca under cProfile and prints the results."""

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
