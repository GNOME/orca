# Orca
#
# Copyright 2005-2009 Sun Microsystems Inc.
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
__copyright__ = "Copyright (c) 2005-2009 Sun Microsystems Inc."
__license__   = "LGPL"

from typing import Any, TYPE_CHECKING

from orca import braille
from orca import braille_generator
from orca import debug
from orca.ax_object import AXObject
from orca.ax_table import AXTable
from orca.ax_text import AXText

if TYPE_CHECKING:
    import gi
    gi.require_version("Atspi", "2.0")
    from gi.repository import Atspi

    from . import script


class BrailleGenerator(braille_generator.BrailleGenerator):
    """Produces braille presentation for accessible objects."""

    # Type annotation to override the base class script type
    _script: script.Script

    @staticmethod
    def log_generator_output(func):
        """Decorator for logging."""

        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            tokens = [f"SOFFICE BRAILLE GENERATOR: {func.__name__}:", result]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return result
        return wrapper

    @log_generator_output
    def _generate_accessible_role(self, obj: Atspi.Accessible, **args) -> list[Any]:
        if self._script.utilities.is_document(obj):
            return []

        return super()._generate_accessible_role(obj, **args)

    @log_generator_output
    def _generate_real_table_cell(self, obj: Atspi.Accessible, **args) -> list[Any]:
        if not self._script.utilities.in_document_content(obj):
            return super()._generate_real_table_cell(obj, **args)

        if not AXObject.get_child_count(obj):
            result = super()._generate_real_table_cell(obj, **args)
        else:
            result = []
            args["formatType"] = "focused"
            for child in AXObject.iter_children(obj):
                result.extend(self.generate(child, **args))

        if not self._script.utilities.is_spreadsheet_cell(obj):
            return result

        object_text = AXText.get_substring(obj, 0, -1)
        cell_name = AXTable.get_label_for_cell_coordinates(obj) \
                or self._script.utilities.spreadsheet_cell_name(obj)
        return [braille.Component(obj, " ".join((object_text, cell_name)))]
