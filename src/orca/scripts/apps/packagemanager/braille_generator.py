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

"""Custom braille generator for Packagemanager."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2009 Sun Microsystems Inc."
__license__   = "LGPL"

import orca.braille_generator as braille_generator

class BrailleGenerator(braille_generator.BrailleGenerator):
    """Special handling to minimize chattiness and maximize accuracy when
    presenting the package list toggle. In particular, the toggle column
    header is now a (de)select all rather than a sort. The PM GUI team
    has provided an accessible name reflective of the new functionality
    for the column header. Unfortunately, that functionality only applies
    when the column header has focus. Therefore, don't present the name
    when in the list proper.
    """

    def __init__(self, script):
        braille_generator.BrailleGenerator.__init__(self, script)

    def _generateColumnHeaderIfToggleAndNoText(self, obj, **args):
        """If this table cell has a "toggle" action, and doesn't have any
        label associated with it then also present the table column header
        Unless we're in the package list.
        """

        result = []
        if not self._script.isPackageListToggle(obj):
            result.extend(braille_generator.BrailleGenerator.\
                _generateColumnHeaderIfToggleAndNoText(self, obj, **args))
        return result
