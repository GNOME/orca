# Orca
#
# Copyright 2005-2008 Sun Microsystems Inc.
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

__id__        = "$Id:$"
__version__   = "$Revision:$"
__date__      = "$Date:$"
__copyright__ = "Copyright (c) 2005-2008 Sun Microsystems Inc."
__license__   = "LGPL"

import pyatspi

import orca.orca as orca
import orca.orca_state as orca_state
import orca.settings as settings
import orca.speech as speech

import orca.scripts.toolkits.Gecko as Gecko

class Script(Gecko.Script):

    def __init__(self, app):
        Gecko.Script.__init__(self, app)

        # By default, don't present if Yelp is not the active application.
        #
        self.presentIfInactive = False

    def onDocumentLoadComplete(self, event):
        """Called when a web page load is completed."""

        # We can't count on this event, but often when the first Yelp
        # window is opened, this event is emitted. If we silently set
        # the locusOfFocus here, the frame won't be the locusOfFocus
        # for the initial call to getDocumentFrame(). As an added
        # bonus, when we detect this condition, we can place the user
        # at the top of the content. Yelp seems to prefer the end,
        # which is confusing non-visually.
        #
        if event.source.getRole() == pyatspi.ROLE_DOCUMENT_FRAME:
            orca.setLocusOfFocus(event, event.source, False)

        return Gecko.Script.onDocumentLoadComplete(self, event)

    def getDocumentFrame(self):
        """Returns the document frame that holds the content being shown."""

        obj = orca_state.locusOfFocus
        #print "getDocumentFrame", obj

        if not obj:
            return None

        role = obj.getRole()
        if role == pyatspi.ROLE_DOCUMENT_FRAME:
            # We caught a lucky break.
            #
            return obj
        elif role == pyatspi.ROLE_FRAME:
            # The window was just activated. Do not look from the top down;
            # it will cause the yelp hierarchy to become crazy, resulting in
            # all future events having an empty name for the application.
            # See bug 356041 for more information.
            #
            return None
        else:
            # We might be in some content. In this case, look up.
            #
            return self.getAncestor(obj,
                                    [pyatspi.ROLE_DOCUMENT_FRAME,
                                     pyatspi.ROLE_EMBEDDED],
                                    [pyatspi.ROLE_FRAME])

    def onCaretMoved(self, event):
        """Called whenever the caret moves.

        Arguments:
        - event: the Event
        """

        # Unlike the unpredictable wild, wild web, odds are good that a
        # caret-moved event from document content in Yelp is valid. But
        # depending upon the locusOfFocus at the time this event is issued
        # the default Gecko toolkit script might not do the right thing.
        # Rather than risk breaking access to web content, we'll just set
        # the locusOfFocus here before sending this event on.
        #
        if self.inDocumentContent(event.source):
            orca.setLocusOfFocus(event, event.source)

        return Gecko.Script.onCaretMoved(self, event)

    def onChildrenChanged(self, event):
        """Called when a child node has changed. When the user follows a
        link in an open Yelp window, the document frame content changes,
        but we don't get any events to tell us something has loaded.
        STILL INVESTIGATING, but it seems like we get a reliable
        object:children-changed:add event for detail1 == -1 for the
        document frame. Let's go with that for now....
        """

        if event.type.startswith("object:children-changed:add") \
           and event.detail1 == -1 and event.source \
           and event.source.getRole() == pyatspi.ROLE_DOCUMENT_FRAME:

            #print "Yelp object:children-changed:add", obj, characterOffset

            # If the frame is the locusOfFocus, getCaretContext() will fail
            # because we don't want to look from the top down to find the
            # document frame and cause Yelp to have an identity crisis. So
            # let's just set it here and avoid that whole mess.
            #
            orca.setLocusOfFocus(event, event.source, False)
            [obj, characterOffset] = self.getCaretContext()
            if obj:
                self.setCaretPosition(obj, characterOffset)
                if obj.getState().contains(pyatspi.STATE_FOCUSED):
                    speech.speakUtterances(\
                        self.speechGenerator.getSpeech(obj, False))
                elif not Gecko.script_settings.sayAllOnLoad:
                    self.speakContents(\
                        self.getLineContentsAtOffset(obj, characterOffset))
                elif settings.enableSpeech:
                    self.sayAll(None)

        else:
            Gecko.Script.onChildrenChanged(self, event)
