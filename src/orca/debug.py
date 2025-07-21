# Orca
#
# Copyright 2005-2008 Sun Microsystems Inc.
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

# pylint: disable=wrong-import-position

"""Handles writing debugging messages to the debug file or stderr."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2008 Sun Microsystems Inc."
__license__   = "LGPL"

import inspect
import traceback
import re
import sys
import threading
from datetime import datetime
from typing import Any, TextIO

from .ax_utilities_debugging import AXUtilitiesDebugging

LEVEL_OFF = 10000
LEVEL_SEVERE = 1000
LEVEL_WARNING = 900
LEVEL_INFO = 800
LEVEL_ALL = 0

# Leave these as-is for now so as not to break debugging for anyone using orca-customizations.py
# pylint: disable=invalid-name
debugLevel: int = LEVEL_SEVERE
debugFile: TextIO | None = None
# pylint: enable=invalid-name

_printing = threading.local()

def print_exception(level: int) -> None:
    """Prints out information regarding the current exception."""
    if level >= debugLevel:
        _print_text(level)
        traceback.print_exc(100, debugFile)
        _print_text(level)

def print_tokens(
    level: int, tokens: list[Any], timestamp: bool = False, stack: bool = False
) -> None:
    """Prints out each token as a human-consumable string."""

    if level < debugLevel:
        return

    text = " ".join(map(AXUtilitiesDebugging.as_string, tokens))
    text = re.sub(r" (?=[,.:)])(?![\n])", "", text)
    _print_text(level, text, timestamp, stack)

def print_message(level: int, text: str, timestamp: bool = False, stack: bool = False) -> None:
    """Prints out text."""

    if level < debugLevel:
        return

    _print_text(level, text, timestamp, stack)

def _stack_as_string(max_frames: int = 4) -> str:
    callers = []
    current_module = inspect.getmodule(inspect.currentframe())
    stack = inspect.stack()
    for i in range(1, len(stack)):
        frame = stack[i]
        module = inspect.getmodule(frame[0])
        if module == current_module:
            continue
        if frame.function == "main":
            continue
        if module is None or module.__name__ is None:
            continue
        callers.append(frame)
        if len(callers) >= max_frames:
            break

    callers.reverse()
    return " > ".join(map(AXUtilitiesDebugging.as_string, callers))

def _print_text(level: int, text: str = "", timestamp: bool = False, stack: bool = False) -> None:
    if level < debugLevel:
        return

    # Prevent reentrancy.
    if getattr(_printing, "active", False):
        return

    _printing.active = True

    if timestamp:
        text = text.replace("\n", f"\n{' ' * 18}")
        text = f"{datetime.now().strftime('%H:%M:%S.%f')} - {text}"
    if stack:
        text += f" {_stack_as_string()}"

    if debugFile:
        try:
            debugFile.writelines([text, "\n"])
        except (AttributeError, OSError):
            _printing.active = False
            return
        except (TypeError, ValueError, UnicodeEncodeError) as error:
            text = f"Exception trying to write text to file: {error}"
            debugFile.writelines([text, "\n"])
    else:
        try:
            sys.stderr.writelines([text, "\n"])
        except (AttributeError, OSError):
            _printing.active = False
            return
        except (TypeError, ValueError, UnicodeEncodeError) as error:
            text = f"Exception trying to write text to stderr: {error}"
            sys.stderr.writelines([text, "\n"])

    _printing.active = False
