# Orca
#
# Copyright 2018-2019 Igalia, S.L.
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

"""Custom speech generator for Chromium."""

# Please note: ATK support in Chromium needs much work. Until that work has been
# done, Orca will not be able to provide access to Chromium. This generator is a
# work in progress.

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2018-2019 Igalia, S.L."
__license__   = "LGPL"

import gi
gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

from orca import debug
from orca.scripts import web
from orca.ax_document import AXDocument
from orca.ax_object import AXObject
from orca.ax_utilities import AXUtilities


class SpeechGenerator(web.SpeechGenerator):

    def __init__(self, script):
        super().__init__(script)

    def _generateNewAncestors(self, obj, **args):
        # Likely a refocused submenu whose functional child was just collapsed.
        # The new ancestors might technically be new, but they are not as far
        # as the user is concerned.
        if self._script.utilities.treatAsMenu(obj):
            tokens = ["CHROMIUM: Not generating new ancestors for", obj]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return []

        return super()._generateNewAncestors(obj, **args)

    def _generateListBoxItemWidgets(self, obj, **args):
        # The list which descends from a combobox should be a menu, and its children
        # menuitems. We can remove this once that change is made in Chromium.
        if AXObject.find_ancestor(obj, AXUtilities.is_combo_box):
            tokens = ["CHROMIUM: Not generating listbox item widgets for combobox child", obj]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return []

        return super()._generateListBoxItemWidgets(obj, **args)

    def _generateLabelOrName(self, obj, **args):
        if AXUtilities.is_frame(obj):
            document = self._script.utilities.activeDocument(obj)
            if document and not AXDocument.get_uri(document):
                # Eliminates including "untitled" in the frame name.
                return super()._generateLabelOrName(AXObject.get_parent(obj))

        return super()._generateLabelOrName(obj, **args)

    def _generateRoleName(self, obj, **args):
        if self._script.utilities.isListItemMarker(obj):
            return []

        return super()._generateRoleName(obj, **args)

    def generateSpeech(self, obj, **args):
        if self._script.utilities.inDocumentContent(obj):
            return super().generateSpeech(obj, **args)

        # TODO - JD: A similar situation seems to exist regarding the role of items in Gtk4.
        oldRole = None
        if self._script.utilities.treatAsMenu(obj):
            tokens = ["CHROMIUM: HACK? Speaking menu item as menu", obj]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            oldRole = self._overrideRole(Atspi.Role.MENU, args)

        result = super().generateSpeech(obj, **args)
        if oldRole is not None:
            self._restoreRole(oldRole, args)

        return result
