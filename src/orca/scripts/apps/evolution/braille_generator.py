# Orca
#
# Copyright (C) 2015 Igalia, S.L.
#
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
__copyright__ = "Copyright (c) 2015 Igalia, S.L."
__license__   = "LGPL"

from typing import Any, TYPE_CHECKING

from orca import braille
from orca import braille_generator
from orca import debug
from orca.scripts import web

if TYPE_CHECKING:
    import gi
    gi.require_version("Atspi", "2.0")
    from gi.repository import Atspi

    from . import script

class BrailleGenerator(web.BrailleGenerator, braille_generator.BrailleGenerator):
    """Produces braille presentation for accessible objects."""

    # Type annotation to override the base class script type
    _script: script.Script

    @staticmethod
    def log_generator_output(func):
        """Decorator for logging."""

        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            tokens = [f"EVOLUTION BRAILLE GENERATOR: {func.__name__}:", result]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return result
        return wrapper

    @log_generator_output
    def _generate_real_active_descendant_displayed_text(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        if self._script.utilities.is_message_list_status_cell(obj):
            return []

        return super()._generate_real_active_descendant_displayed_text(obj, **args)

    def generate_braille(self, obj: Atspi.Accessible, **args) -> list[Any]:
        result, focused_region = super().generate_braille(obj, **args)
        if not result or focused_region != result[0]:
            return [result, focused_region]

        def has_obj(x):
            return isinstance(x, (braille.Component, braille.Text))

        def is_obj(x):
            return obj == x.accessible

        matches = [r for r in result if has_obj(r) and is_obj(r)]
        if matches:
            focused_region = matches[0]

        return [result, focused_region]
