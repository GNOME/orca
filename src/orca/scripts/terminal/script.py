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

from orca import debug
from orca import orca
from orca import orca_state
from orca import speech
from orca.scripts import default

from .braille_generator import BrailleGenerator
from .speech_generator import SpeechGenerator
from .script_utilities import Utilities


class Script(default.Script):

    def __init__(self, app):
        super().__init__(app)
        self.presentIfInactive = False

    def deactivate(self):
        """Called when this script is deactivated."""

        self.utilities.clearCache()
        super().deactivate()

    def getBrailleGenerator(self):
        """Returns the braille generator for this script."""

        return BrailleGenerator(self)

    def getSpeechGenerator(self):
        """Returns the speech generator for this script."""

        return SpeechGenerator(self)

    def getUtilities(self):
        """Returns the utilites for this script."""

        return Utilities(self)

    def onFocus(self, event):
        """Callback for focus: accessibility events."""

        # https://bugzilla.gnome.org/show_bug.cgi?id=748311
        orca.setLocusOfFocus(event, event.source)

    def onTextDeleted(self, event):
        """Callback for object:text-changed:delete accessibility events."""

        if self.utilities.treatEventAsNoise(event):
            msg = "TERMINAL: Deletion is believed to be noise"
            debug.println(debug.LEVEL_INFO, msg, True)
            return

        super().onTextDeleted(event)

    def onTextInserted(self, event):
        """Callback for object:text-changed:insert accessibility events."""

        if not self.utilities.treatEventAsCommand(event):
            super().onTextInserted(event)
            return

        msg = "TERMINAL: Insertion is believed to be due to terminal command"
        debug.println(debug.LEVEL_INFO, msg, True)

        self.updateBraille(event.source)

        newString = self.utilities.insertedText(event)
        if len(newString) == 1:
            self.speakCharacter(newString)
        else:
            voice = self.speechGenerator.voice(string=newString)
            speech.speak(newString, voice)

        if self.flatReviewContext:
            return

        try:
            text = event.source.queryText()
        except:
            pass
        else:
            self._saveLastCursorPosition(event.source, text.caretOffset)
            self.utilities.updateCachedTextSelection(event.source)

    def presentKeyboardEvent(self, event):
        if orca_state.learnModeEnabled or not event.isPrintableKey():
            return super().presentKeyboardEvent(event)

        if event.isPressedKey():
            return False

        self._sayAllIsInterrupted = False
        self.utilities.clearCachedCommandState()
        if event.shouldEcho == False or event.isOrcaModified() or event.isCharacterEchoable():
            return False

        # We have no reliable way of knowing a password is being entered into
        # a terminal -- other than the fact that the text typed isn't there.
        try:
            text = event.getObject().queryText()
            offset = text.caretOffset
            prevChar = text.getText(offset - 1, offset)
            char = text.getText(offset, offset + 1)
        except:
            return False

        string = event.event_string
        if string not in [prevChar, "space", char]:
            return False

        msg = "TERMINAL: Presenting keyboard event %s" % string
        debug.println(debug.LEVEL_INFO, msg, True)

        voice = self.speechGenerator.voice(string=string)
        speech.speakKeyEvent(event, voice)
        return True

    def skipObjectEvent(self, event):
        if event.type == "object:text-changed:insert":
            return False

        newEvent, newTime = None, 0
        if event.type == "object:text-changed:delete":
            if self.utilities.isBackSpaceCommandTextDeletionEvent(event):
                return False

            newEvent, newTime = self.eventCache.get("object:text-changed:insert")

        if newEvent is None or newEvent.source != event.source:
            return super().skipObjectEvent(event)

        if event.detail1 != newEvent.detail1:
            return False

        data = "\n%s%s" % (" " * 11, str(newEvent).replace("\t", " " * 11))
        msg = "TERMINAL: Skipping due to more recent event at offset%s" % data
        debug.println(debug.LEVEL_INFO, msg, True)
        return True
