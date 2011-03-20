# Orca
#
# Copyright (C) 2010 Joanmarie Diggs
#
# Author: Joanmarie Diggs <joanied@gnome.org>
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
__copyright__ = "Copyright (c) 2010 Joanmarie Diggs"
__license__   = "LGPL"

import pyatspi

import orca.scripts.default as default
import orca.orca as orca
import orca.orca_state as orca_state
import orca.speech as speech
from orca.orca_i18n import _

from structural_navigation import StructuralNavigation
from braille_generator import BrailleGenerator
from speech_generator import SpeechGenerator
from script_utilities import Utilities

########################################################################
#                                                                      #
# The WebKitGtk script class.                                          #
#                                                                      #
########################################################################

class Script(default.Script):

    CARET_NAVIGATION_KEYS = ['Left', 'Right', 'Up', 'Down', 'Home', 'End']

    def __init__(self, app):
        """Creates a new script for WebKitGtk applications.

        Arguments:
        - app: the application to create a script for.
        """

        default.Script.__init__(self, app)
        self._loadingDocumentContent = False

    def getListeners(self):
        """Sets up the AT-SPI event listeners for this script."""

        listeners = default.Script.getListeners(self)

        listeners["document:reload"]                        = \
            self.onDocumentReload
        listeners["document:load-complete"]                 = \
            self.onDocumentLoadComplete
        listeners["document:load-stopped"]                  = \
            self.onDocumentLoadStopped
        listeners["object:state-changed:busy"]              = \
            self.onStateChanged

        return listeners

    def setupInputEventHandlers(self):
        """Defines InputEventHandler fields for this script that can be
        called by the key and braille bindings."""

        default.Script.setupInputEventHandlers(self)
        self.inputEventHandlers.update(
            self.structuralNavigation.inputEventHandlers)

    def getKeyBindings(self):
        """Defines the key bindings for this script. Setup the default
        key bindings, then add one in for reading the input line.

        Returns an instance of keybindings.KeyBindings.
        """

        keyBindings = default.Script.getKeyBindings(self)
        bindings = self.structuralNavigation.keyBindings
        for keyBinding in bindings.keyBindings:
            keyBindings.add(keyBinding)

        return keyBindings

    def getBrailleGenerator(self):
        """Returns the braille generator for this script."""

        return BrailleGenerator(self)

    def getSpeechGenerator(self):
        """Returns the speech generator for this script."""

        return SpeechGenerator(self)

    def getStructuralNavigation(self):
        """Returns the 'structural navigation' class for this script."""

        types = self.getEnabledStructuralNavigationTypes()
        return StructuralNavigation(self, types, True)

    def getUtilities(self):
        """Returns the utilites for this script."""

        return Utilities(self)

    def onCaretMoved(self, event):
        """Called whenever the caret moves.

        Arguments:
        - event: the Event
        """

        lastKey, mods = self.utilities.lastKeyAndModifiers()
        if lastKey in ['Tab', 'ISO_Left_Tab']:
            return

        if self.utilities.isWebKitGtk(orca_state.locusOfFocus):
            orca.setLocusOfFocus(event, event.source, False)

        default.Script.onCaretMoved(self, event)

    def onDocumentReload(self, event):
        """Called when the reload button is hit for a web page."""

        if event.source.getRole() == pyatspi.ROLE_DOCUMENT_FRAME:
            self._loadingDocumentContent = True

    def onDocumentLoadComplete(self, event):
        """Called when a web page load is completed."""

        if event.source.getRole() == pyatspi.ROLE_DOCUMENT_FRAME:
            self._loadingDocumentContent = False

    def onDocumentLoadStopped(self, event):
        """Called when a web page load is interrupted."""

        if event.source.getRole() == pyatspi.ROLE_DOCUMENT_FRAME:
            self._loadingDocumentContent = False

    def onFocus(self, event):
        """Called whenever an object gets focus.

        Arguments:
        - event: the Event
        """

        obj = event.source
        role = obj.getRole()
        if role == pyatspi.ROLE_LIST_ITEM and obj.childCount:
            return

        textRoles = [pyatspi.ROLE_HEADING,
                     pyatspi.ROLE_PANEL,
                     pyatspi.ROLE_PARAGRAPH,
                     pyatspi.ROLE_SECTION]
        if role in textRoles:
            return

        if role == pyatspi.ROLE_LINK and obj.childCount:
            try:
                text = obj.queryText()
            except NotImplementedError:
                orca.setLocusOfFocus(event, obj[0])

        default.Script.onFocus(self, event)

    def onStateChanged(self, event):
        """Called whenever an object's state changes.

        Arguments:
        - event: the Event
        """

        if not event.type.startswith("object:state-changed:busy"):
            default.Script.onStateChanged(self, event)
            return

        if not event.source \
           or event.source.getRole() != pyatspi.ROLE_DOCUMENT_FRAME:
            return

        if event.detail1:
            # Translators: this is in reference to loading a web page
            # or some other content.
            #
            self.presentMessage(_("Loading.  Please wait."))
        elif event.source.name:
            # Translators: this is in reference to loading a web page
            # or some other content.
            #
            self.presentMessage(_("Finished loading %s.") % event.source.name)
        else:
            # Translators: this is in reference to loading a web page
            # or some other content.
            #
            self.presentMessage(_("Finished loading."))

    def onTextSelectionChanged(self, event):
        """Called when an object's text selection changes.

        Arguments:
        - event: the Event
        """

        # The default script's method attempts to handle various and sundry
        # complications that simply do not apply here.
        #
        spokenRange = self.pointOfReference.get("spokenTextRange") or [0, 0]
        startOffset, endOffset = spokenRange

        self.speakTextSelectionState(event.source, startOffset, endOffset)

    def sayCharacter(self, obj):
        """Speak the character at the caret.

        Arguments:
        - obj: an Accessible object that implements the AccessibleText
          interface
        """

        if obj.getRole() == pyatspi.ROLE_SEPARATOR:
            speech.speak(self.speechGenerator.generateSpeech(obj))
            return

        default.Script.sayCharacter(self, obj)

    def sayLine(self, obj):
        """Speaks the line of an AccessibleText object that contains the
        caret.

        Arguments:
        - obj: an Accessible object that implements the AccessibleText
               interface
        """

        default.Script.sayLine(self, obj)

        rolesToSpeak = [pyatspi.ROLE_HEADING]
        if obj.getRole() in rolesToSpeak:
            speech.speak(self.speechGenerator.getRoleName(obj))

    def skipObjectEvent(self, event):
        """Gives us, and scripts, the ability to decide an event isn't
        worth taking the time to process under the current circumstances.

        Arguments:
        - event: the Event

        Returns True if we shouldn't bother processing this object event.
        """

        if event.type.startswith('object:state-changed:focused') \
           and event.detail1:
            if event.source.getRole() == pyatspi.ROLE_LINK:
                return False

            lastKey, mods = self.utilities.lastKeyAndModifiers()
            if lastKey in self.CARET_NAVIGATION_KEYS:
                return True

        return default.Script.skipObjectEvent(self, event)

    def useStructuralNavigationModel(self):
        """Returns True if we should do our own structural navigation.
        This should return False if we're in a form field, or not in
        document content.
        """

        doNotHandleRoles = [pyatspi.ROLE_ENTRY,
                            pyatspi.ROLE_TEXT,
                            pyatspi.ROLE_PASSWORD_TEXT,
                            pyatspi.ROLE_LIST,
                            pyatspi.ROLE_LIST_ITEM,
                            pyatspi.ROLE_MENU_ITEM]

        if not self.structuralNavigation.enabled:
            return False

        if not self.utilities.isWebKitGtk(orca_state.locusOfFocus):
            return False

        if orca_state.locusOfFocus.getRole() in doNotHandleRoles:
            states = orca_state.locusOfFocus.getState()
            if states.contains(pyatspi.STATE_FOCUSED):
                return False

        return True
