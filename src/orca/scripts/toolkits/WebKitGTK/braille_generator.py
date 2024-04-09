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

"""Custom braille generator for WebKitGTK."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2024 Igalia, S.L." \
                "Copyright (c) 2024 GNOME Foundation Inc."
__license__   = "LGPL"

from orca import braille_generator
from orca import debug
from orca.scripts import web

class BrailleGenerator(web.BrailleGenerator):
    """Custom braille generator for WebKitGTK."""

    def generateBraille(self, obj, **args):
        """Generates braille for obj."""

        if self._script.utilities.inDocumentContent(obj):
            return super().generateBraille(obj, **args)

        msg = "WEBKITGTK: Using default braille generator"
        debug.printMessage(debug.LEVEL_INFO, msg, True)
        return braille_generator.BrailleGenerator.generateBraille(self, obj, **args)
