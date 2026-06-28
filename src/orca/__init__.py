"""Orca Screen Reader"""

from __future__ import annotations

import os

_ORCA_DIR = os.path.dirname(os.path.realpath(__file__))


def is_orca(filename: str, module_prefix: str = "") -> bool:
    """Return True if filename is Orca code, optionally matching module_prefix."""

    filepath = os.path.realpath(filename) if filename else ""
    module_name = os.path.splitext(os.path.basename(filepath))[0] if filepath else ""
    try:
        is_orca_code = os.path.commonpath([_ORCA_DIR, filepath]) == _ORCA_DIR
    except ValueError:
        return False

    return is_orca_code and (not module_prefix or module_name.startswith(module_prefix))
