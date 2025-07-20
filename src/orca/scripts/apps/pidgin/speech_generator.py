# Orca
#
# Copyright 2004-2009 Sun Microsystems Inc.
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

"""Produces speech presentation for accessible objects."""

# This has to be the first non-docstring line in the module to make linters happy.
from __future__ import annotations

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2004-2009 Sun Microsystems Inc."
__license__   = "LGPL"

from typing import Any, TYPE_CHECKING

import gi
gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

from orca import debug
from orca import speech_generator

if TYPE_CHECKING:
    from . import script

class SpeechGenerator(speech_generator.SpeechGenerator):
    """Produces speech presentation for accessible objects."""

    # Type annotation to override the base class script type
    _script: script.Script

    @staticmethod
    def log_generator_output(func):
        """Decorator for logging."""

        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            tokens = [f"PIDGIN SPEECH GENERATOR: {func.__name__}:", result]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return result
        return wrapper

    @log_generator_output
    def _generate_state_expanded(self, obj: Atspi.Accessible, **args) -> list[Any]:
        cell = self._script.utilities.get_expander_cell_for(obj) or obj
        return super()._generate_state_expanded(cell, **args)

    @log_generator_output
    def _generate_number_of_children(self, obj: Atspi.Accessible, **args) -> list[Any]:
        cell = self._script.utilities.get_expander_cell_for(obj) or obj
        return super()._generate_number_of_children(cell, **args)
