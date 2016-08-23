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

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2016 Igalia, S.L."
__license__   = "LGPL"

import pyatspi

from orca import debug
from orca import keybindings
from orca import script_utilities
from orca import settings_manager

_settingsManager = settings_manager.getManager()


class Utilities(script_utilities.Utilities):

    def __init__(self, script):
        super().__init__(script)

    def clearCache(self):
        pass

    def insertedText(self, event):
        if len(event.any_data) == 1:
            return event.any_data

        try:
            text = event.source.queryText()
        except:
            msg = "ERROR: Exception querying text for %s" % event.source
            debug.println(debug.LEVEL_INFO, msg, True)
            return event.any_data

        start, end = event.detail1, event.detail1 + len(event.any_data)
        boundary = pyatspi.TEXT_BOUNDARY_LINE_START

        firstLine = text.getTextAtOffset(start, boundary)
        if firstLine != ("", 0, 0):
            start = firstLine[1]

        lastLine = text.getTextAtOffset(end - 1, boundary)
        if lastLine != ("", 0, 0):
            end = min(lastLine[2], text.caretOffset)

        return text.getText(start, end)

    def isTextArea(self, obj):
        return True

    def treatEventAsTerminalCommand(self, event):
        if self.lastInputEventWasCommand():
            return True

        if event.type.startswith("object:text-changed:insert") and event.any_data.strip():
            keyString, mods = self.lastKeyAndModifiers()
            if keyString in ["Return", "Tab", "space", " "]:
                return True
            if mods & keybindings.ALT_MODIFIER_MASK:
                return True
            if len(event.any_data) > 1 and self.lastInputEventWasPrintableKey():
                return True

        return False

    def treatEventAsTerminalNoise(self, event):
        if self.lastInputEventWasCommand():
            return False

        if event.type.startswith("object:text-changed:delete") and event.any_data.strip():
            keyString, mods = self.lastKeyAndModifiers()
            if keyString in ["Return", "Tab", "space", " "]:
                return True
            if mods & keybindings.ALT_MODIFIER_MASK:
                return True
            if len(event.any_data) > 1 and self.lastInputEventWasPrintableKey():
                return True

        return False

    def willEchoCharacter(self, event):
        if not _settingsManager.getSetting("enableEchoByCharacter"):
            return False

        if len(event.event_string) != 1 \
           or event.modifiers & keybindings.ORCA_CTRL_MODIFIER_MASK:
            return False

        return True
