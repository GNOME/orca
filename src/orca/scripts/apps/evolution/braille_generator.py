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

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2015 Igalia, S.L."
__license__   = "LGPL"

import orca.braille as braille
import orca.scripts.toolkits.WebKitGtk as WebKitGtk

class BrailleGenerator(WebKitGtk.BrailleGenerator):

    def __init__(self, script):
        super().__init__(script)
        self._cache = {}

    def _isMessageListToggleCell(self, obj):
        cached = self._cache.get(hash(obj), {})
        rv = cached.get("isMessageListToggleCell")
        if rv == None:
            rv = self._script.utilities.isMessageListToggleCell(obj)
            cached["isMessageListToggleCell"] = rv
            self._cache[hash(obj)] = cached

        return rv

    def _generateRealActiveDescendantDisplayedText(self, obj, **args):
        if self._isMessageListToggleCell(obj):
            return []

        return super()._generateRealActiveDescendantDisplayedText(obj, **args)

    def generateBraille(self, obj, **args):
        self._cache = {}
        result, focusedRegion = super().generateBraille(obj, **args)
        self._cache = {}

        if not result or focusedRegion != result[0]:
            return [result, focusedRegion]

        hasObj = lambda x: isinstance(x, (braille.Component, braille.Text))
        isObj = lambda x: self._script.utilities.isSameObject(obj, x.accessible)
        matches = [r for r in result if hasObj(r) and isObj(r)]
        if matches:
            focusedRegion = matches[0]

        return [result, focusedRegion]
