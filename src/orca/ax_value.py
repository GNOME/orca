# Orca
#
# Copyright 2024 Igalia, S.L.
# Copyright 2024 GNOME Foundation Inc.
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

# pylint: disable=broad-exception-caught
# pylint: disable=wrong-import-position

"""
Utilities for obtaining value-related information about accessible objects.
These utilities are app-type- and toolkit-agnostic. Utilities that might have
different implementations or results depending on the type of app (e.g. terminal,
chat, web) or toolkit (e.g. Qt, Gtk) should be in script_utilities.py file(s).

N.B. There are currently utilities that should never have custom implementations
that live in script_utilities.py files. These will be moved over time.
"""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2024 Igalia, S.L." \
                "Copyright (c) 2024 GNOME Foundation Inc."
__license__   = "LGPL"

import threading
import time

import gi
gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

from . import debug
from .ax_object import AXObject
from .ax_utilities import AXUtilities

class AXValue:
    """Utilities for obtaining value-related information about accessible objects."""

    LAST_KNOWN_VALUE = {}
    _lock = threading.Lock()

    @staticmethod
    def _clear_stored_data():
        """Clears any data we have cached for objects"""

        while True:
            time.sleep(60)
            msg = "AXValue: Clearing local cache."
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            AXValue.LAST_KNOWN_VALUE.clear()

    @staticmethod
    def start_cache_clearing_thread():
        """Starts thread to periodically clear cached details."""

        thread = threading.Thread(target=AXValue._clear_stored_data)
        thread.daemon = True
        thread.start()

    @staticmethod
    def did_value_change(obj):
        """Returns True if the current value changed."""

        if not AXObject.supports_value(obj):
            return False

        old_value = AXValue.LAST_KNOWN_VALUE.get(hash(obj))
        result = old_value != AXValue._get_current_value(obj)
        if result:
            tokens = ["AXValue: Previous value of", obj, f"was {old_value}"]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)

        return result

    @staticmethod
    def _get_current_value(obj):
        """Returns the current value of obj."""

        if not AXObject.supports_value(obj):
            return 0

        try:
            value = Atspi.Value.get_current_value(obj)
        except Exception as error:
            msg = f"AXValue: Exception in _get_current_value: {error}"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return 0

        tokens = ["AXValue: Current value of", obj, f"is {value}"]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
        return value

    @staticmethod
    def get_current_value(obj):
        """Returns the current value of obj."""

        if not AXObject.supports_value(obj):
            return 0

        value = AXValue._get_current_value(obj)
        AXValue.LAST_KNOWN_VALUE[hash(obj)] = value
        return value

    @staticmethod
    def get_current_value_text(obj):
        """Returns the app-provided text-alternative for the current value of obj."""

        text = AXObject.get_attribute(obj, "valuetext", False) or ""
        if text:
            tokens = ["AXValue: valuetext attribute for", obj, f"is '{text}'"]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return text

        if not AXObject.supports_value(obj):
            return ""

        try:
            value = Atspi.Value.get_text(obj)
        except Exception as error:
            msg = f"AXValue: Exception in get_current_value_text: {error}"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            value = ""

        tokens = ["AXValue: Value text of", obj, f"is '{value}'"]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
        if value:
            return value

        current = AXValue._get_current_value(obj)
        if abs(current) < 1 and current != 0:
            str_current = str(current)
            decimal_places = len(str_current.split('.')[1])
        else:
            decimal_places = 0

        return f"{current:.{decimal_places}f}"

    @staticmethod
    def get_value_as_percent(obj):
        """Returns the current value as a percent, or None if that is not applicable."""

        if not AXObject.supports_value(obj):
            return None

        value = AXValue._get_current_value(obj)
        if AXUtilities.is_indeterminate(obj) and value <= 0:
            tokens = ["AXValue:", obj, "has state indeterminate"]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return None

        minimum = AXValue.get_minimum_value(obj)
        maximum = AXValue.get_maximum_value(obj)
        if minimum == maximum:
            return None

        result = int((value / (maximum - minimum)) * 100)
        tokens = ["AXValue: Current value of", obj, f"as percent is is {result}"]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
        return result

    @staticmethod
    def get_minimum_value(obj):
        """Returns the minimum value of obj."""

        if not AXObject.supports_value(obj):
            return 0

        try:
            value = Atspi.Value.get_minimum_value(obj)
        except Exception as error:
            msg = f"AXValue: Exception in get_minimum_value: {error}"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return 0

        tokens = ["AXValue: Minimum value of", obj, f"is {value}"]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
        return value

    @staticmethod
    def get_maximum_value(obj):
        """Returns the maximum value of obj."""

        if not AXObject.supports_value(obj):
            return 0

        try:
            value = Atspi.Value.get_maximum_value(obj)
        except Exception as error:
            msg = f"AXValue: Exception in get_maximum_value: {error}"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return 0

        tokens = ["AXValue: Maximum value of", obj, f"is {value}"]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
        return value

AXValue.start_cache_clearing_thread()
