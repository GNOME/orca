# Orca
#
# Copyright 2005-2010 Sun Microsystems Inc.
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Library General Public
# License as published by the Free Software Foundation; either
# version 2 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Library General Public License for more details.
#
# You should have received a copy of the GNU Library General Public
# License along with this library; if not, write to the
# Free Software Foundation, Inc., Franklin Street, Fifth Floor,
# Boston MA  02110-1301 USA.

"""Custom script for Yelp."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2010 Sun Microsystems Inc."
__license__   = "LGPL"

import gtk
import pyatspi

import orca.orca as orca
import orca.settings as settings
import orca.speech as speech

import orca.scripts.toolkits.Gecko as Gecko

import script_settings
from script_utilities import Utilities

class Script(Gecko.Script):

    def __init__(self, app):
        Gecko.Script.__init__(self, app)

        # By default, don't present if Yelp is not the active application.
        #
        self.presentIfInactive = False

        # Each time the user presses Return on a link, we get all the events
        # associated with a page loading -- even if the link is to an anchor
        # on the same page. We don't want to move to the top of the page and
        # do a SayAll unless we have a new page. We'll use the frame name as
        # a way to identify this condition.
        #
        self._currentFrameName = ""

        # When the user presses Escape to leave the Find tool bar, we do not
        # seem to get any events for the document frame reclaiming focus. If
        # we try to get the caret context, documentFrame() returns None.
        # Store a copy of the context so that we can return it.
        #
        self.lastFindContext = [None, -1]

    def getUtilities(self):
        """Returns the utilites for this script."""

        return Utilities(self)

    def getAppPreferencesGUI(self):
        """Return a GtkVBox contain the application unique configuration
        GUI items for the current application.
        """

        vbox = Gecko.Script.getAppPreferencesGUI(self)

        # We need to maintain a separate setting for grabFocusOnAncestor
        # because the version of Gecko used by Yelp might be different
        # from that used by Firefox. See bug 608149.
        #
        gtk.ToggleButton.set_active(self.grabFocusOnAncestorCheckButton,
                                    script_settings.grabFocusOnAncestor)

        return vbox

    def setAppPreferences(self, prefs):
        """Write out the application specific preferences lines and set the
        new values.

        Arguments:
        - prefs: file handle for application preferences.
        """

        Gecko.Script.setAppPreferences(self, prefs)

        # Write the Yelp specific settings.
        #
        prefix = "orca.scripts.apps.yelp.script_settings"

        value = self.grabFocusOnAncestorCheckButton.get_active()
        prefs.writelines("%s.grabFocusOnAncestor = %s\n" % (prefix, value))
        script_settings.grabFocusOnAncestor = value

    def onCaretMoved(self, event):
        """Called whenever the caret moves.

        Arguments:
        - event: the Event
        """

        if self.utilities.inFindToolbar() \
           and not self.utilities.inFindToolbar(event.source):
            self.lastFindContext = [event.source, event.detail1]

        # Unlike the unpredictable wild, wild web, odds are good that a
        # caret-moved event from document content in Yelp is valid. But
        # depending upon the locusOfFocus at the time this event is issued
        # the default Gecko toolkit script might not do the right thing.
        # Rather than risk breaking access to web content, we'll just set
        # the locusOfFocus here before sending this event on.
        #
        elif self.inDocumentContent(event.source):
            obj = event.source
            characterOffset = event.detail1

            # If the event is for an anchor with no text, try to find
            # something more meaningful.
            #
            while obj and obj.getRole() == pyatspi.ROLE_LINK \
                  and not self.utilities.queryNonEmptyText(obj):
                [obj, characterOffset] = \
                    self.findNextCaretInOrder(obj, characterOffset)

            # We need to notify the presentation managers because we don't
            # seem to get any focus/focused events for links. We seem to
            # get caret-moved events for anchors only when the user has
            # followed a link. Changes in the content being displayed is
            # handled by onStateChanged(). Therefore, we need to notify the
            # presentation managers if this event is not for an empty anchor.
            #
            notify = self.utilities.isSameObject(event.source, obj)
            orca.setLocusOfFocus(
                event, obj, notifyPresentationManager=notify)
            self.setCaretPosition(obj, characterOffset)

        return Gecko.Script.onCaretMoved(self, event)

    def onChildrenChanged(self, event):
        """Called when a child node has changed.  The document frame emits
        these events quite a bit, each time the page changes. We want to
        ignore those events.
        """

        if event.source.getRole() != pyatspi.ROLE_DOCUMENT_FRAME:
            Gecko.Script.onChildrenChanged(self, event)

    def onStateChanged(self, event):
        """Called whenever an object's state changes.

        Arguments:
        - event: the Event
        """

        # When the Find toolbar gives up focus because the user closed
        # it, Yelp's normal behavior is often to give focus to something
        # not especially useful to a user who is blind, like the Back
        # button. For now, let's stop that from happening.
        #
        if event.type.startswith("object:state-changed:showing") \
           and not event.detail1 \
           and self.utilities.inFindToolbar(event.source):
            [obj, characterOffset] = self.lastFindContext
            self.lastFindContext = [None, -1]
            self.setCaretPosition(obj, characterOffset)

        if event.type.startswith("object:state-changed:busy") \
           and event.source.getRole() == pyatspi.ROLE_DOCUMENT_FRAME \
           and not event.detail1:

            # We need to set the locusOfFocus to the document frame in
            # order to reliably get the caret context.
            #
            orca.setLocusOfFocus(
                event, event.source, notifyPresentationManager=False)
            [obj, characterOffset] = self.getCaretContext()

            # Often the first object is an anchor with no text. Try to
            # find something more meaningful and set the caret there.
            #
            while obj and obj.getRole() == pyatspi.ROLE_LINK \
                  and not self.utilities.queryNonEmptyText(obj):
                [obj, characterOffset] = \
                    self.findNextCaretInOrder(obj, characterOffset)

            if not obj:
                return

            if event.source.name == self._currentFrameName:
                orca.setLocusOfFocus(event, obj)
            else:
                self._currentFrameName = event.source.name
                self.setCaretPosition(obj, characterOffset)
                # Pylint thinks that obj is an instance of a list. It most
                # certainly is not. Silly pylint.
                #
                # pylint: disable-msg=E1103
                #
                if obj.getState().contains(pyatspi.STATE_FOCUSED):
                    speech.speak(self.speechGenerator.generateSpeech(obj))
                elif not Gecko.script_settings.sayAllOnLoad:
                    self.speakContents(\
                        self.getLineContentsAtOffset(obj, characterOffset))
                elif settings.enableSpeech:
                    self.sayAll(None)

            return

        Gecko.Script.onStateChanged(self, event)
