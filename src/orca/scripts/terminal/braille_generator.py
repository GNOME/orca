# Orca
#
# Copyright 2016 Igalia, S.L.
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


"""Produces braille presentation for accessible objects."""

# This has to be the first non-docstring line in the module to make linters happy.
from __future__ import annotations

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2016 Igalia, S.L."
__license__   = "LGPL"

from typing import Any, TYPE_CHECKING

from orca import braille_generator
from orca import debug

if TYPE_CHECKING:
    import gi
    gi.require_version("Atspi", "2.0")
    from gi.repository import Atspi


class BrailleGenerator(braille_generator.BrailleGenerator):
    """Produces braille presentation for accessible objects."""

    @staticmethod
    def log_generator_output(func):
        """Decorator for logging."""

        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            tokens = [f"TERMINAL BRAILLE GENERATOR: {func.__name__}:", result]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return result
        return wrapper

    @log_generator_output
    def _generate_accessible_description(self, _obj: Atspi.Accessible, **_args) -> list[Any]:
        # The text in the description is the same as the text in the page
        # tab and similar to (and sometimes the same as) the prompt.
        return []
