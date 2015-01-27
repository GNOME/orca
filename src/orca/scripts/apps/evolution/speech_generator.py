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

import pyatspi

import orca.scripts.toolkits.WebKitGtk as WebKitGtk

class SpeechGenerator(WebKitGtk.SpeechGenerator):

    def __init__(self, script):
        super().__init__(script)
        self._cache = {}

    def _isTreeTableCell(self, obj):
        cached = self._cache.get(hash(obj), {})
        rv = cached.get("isTreeTableCell")
        if rv == None:
            rv = obj.parent and obj.parent.getRole() == pyatspi.ROLE_TREE_TABLE
            cached["isTreeTableCell"] = rv
            self._cache[hash(obj)] = cached

        return rv

    def _isMessageListStatusCell(self, obj):
        cached = self._cache.get(hash(obj), {})
        rv = cached.get("isMessageListStatusCell")
        if rv == None:
            rv = self._script.utilities.isMessageListStatusCell(obj)
            cached["isMessageListStatusCell"] = rv
            self._cache[hash(obj)] = cached

        return rv

    def _isMessageListToggleCell(self, obj):
        cached = self._cache.get(hash(obj), {})
        rv = cached.get("isMessageListToggleCell")
        if rv == None:
            rv = self._script.utilities.isMessageListToggleCell(obj)
            cached["isMessageListToggleCell"] = rv
            self._cache[hash(obj)] = cached

        return rv

    def _isFocused(self, obj):
        cached = self._cache.get(hash(obj), {})
        rv = cached.get("isFocused")
        if rv == None:
            rv = obj.getState().contains(pyatspi.STATE_FOCUSED)
            cached["isFocused"] = rv
            self._cache[hash(obj)] = cached

        return rv

    def _isChecked(self, obj):
        cached = self._cache.get(hash(obj), {})
        rv = cached.get("isChecked")
        if rv == None:
            rv = obj.getState().contains(pyatspi.STATE_CHECKED)
            cached["isChecked"] = rv
            self._cache[hash(obj)] = cached

        return rv

    def _isInNewRow(self, obj):
        cached = self._cache.get(hash(obj), {})
        rv = cached.get("isInNewRow")
        if rv == None:
            row, column = self._script.utilities.coordinatesForCell(obj)
            lastRow = self._script.pointOfReference.get("lastRow")
            rv = row != lastRow
            cached["isInNewRow"] = rv
            self._cache[hash(obj)] = cached

        return rv

    def _generateCellCheckedState(self, obj, **args):
        if self._isMessageListStatusCell(obj):
            return []

        if self._isMessageListToggleCell(obj):
            if self._isInNewRow(obj) or not self._isFocused(obj):
                return []

        return super()._generateCellCheckedState(obj, **args)

    def _generateLabel(self, obj, **args):
        if self._isMessageListToggleCell(obj):
            return []

        return super()._generateLabel(obj, **args)

    def _generateName(self, obj, **args):
        if self._isMessageListToggleCell(obj) \
           and not self._isMessageListStatusCell(obj):
            return []

        return super()._generateName(obj, **args)

    def _generateLabelOrName(self, obj, **args):
        if self._isMessageListToggleCell(obj) \
           and not self._isMessageListStatusCell(obj):
            return []

        return super()._generateLabelOrName(obj, **args)

    def _generateRealActiveDescendantDisplayedText(self, obj, **args):
        if self._isMessageListToggleCell(obj) \
           and not self._isMessageListStatusCell(obj):
            if not self._isChecked(obj):
                return []
            if self._isFocused(obj) and not self._isInNewRow(obj):
                return []

        return super()._generateRealActiveDescendantDisplayedText(obj, **args)

    def _generateRoleName(self, obj, **args):
        if self._isMessageListToggleCell(obj) and not self._isFocused(obj):
            return []

        return super()._generateRoleName(obj, **args)

    def _generateUnselectedCell(self, obj, **args):
        if self._isMessageListToggleCell(obj) or self._isTreeTableCell(obj):
            return []

        return super()._generateUnselectedCell(obj, **args)

    def generateSpeech(self, obj, **args):
        self._cache = {}
        results = super().generateSpeech(obj, **args)
        self._cache = {}

        return results
