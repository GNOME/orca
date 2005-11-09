# Orca
#
# Copyright 2004 Sun Microsystems Inc.
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
# Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.

from orca import a11y
from orca import rolenames
from orca import speech

from orca.orca_i18n import _

from orca.default import Default

########################################################################
#                                                                      #
# The factory method for this module.  All Scripts are expected to     #
# have this method, and it is the sole way that instances of scripts   #
# should be created.                                                   #
#                                                                      #
########################################################################

def getScript(app):
    return Gecko(app)


########################################################################
#                                                                      #
# The Gecko script class.                                              #
#                                                                      #
########################################################################

class Gecko(Default):
    def __init__(self, app):
        Default.__init__(self, app)

        self.listeners["object:link-selected"] = self.onLinkSelected

    def sayAll():
        global activePage
        global sayAllObjects
        global sayAllObjectIndex
        global sayAllObjectCount

        # If there is no active page, we can't do say all
        #
        if activePage is None:
            speech.speak(_("No page to read."))
            return

        # Get all the objects on the page
        #
        try:
            sayAllObjects = a11y.getObjects(activePage)
        except:
            speech.speak(_("Reading web page failed."))
            return

        # Set up say all mode
        #
        sayAllObjectCount = len(sayAllObjects)
        sayAllObjectIndex = 0

        # Speak the name of the page, then start say all mode.  When the
        # name of the page has finished speaking, say all mode will be
        # active and the first chunk of the page will be read
        #
        speech.speak(activePage.name)

        
    # This function is called whenever an object within Mozilla receives
    # focus
    def onFocus(self, event):

        if event.source.role != rolenames.ROLE_PANEL:
            return Default.onFocus(self, event)
    
        # If it's not a panel, do the default
        #
        Default.onFocus(self, event)

        # If the panel has no name, don't touch it
        #
        if len(event.source.name) == 0:
            return

        self.activePage = event.source


    # This function is called when a hyperlink is selected - This happens
    # when a link is navigated to using tab/shift-tab
    def onLinkSelected(event):
        txt = event.source.text
        if txt is None:
            speech.speak(_("link"), "hyperlink")
        else:
            text = txt.getText(0, -1)
            speech.speak(text, "hyperlink")


# The Mozilla version of say all reads text from multiple objects

sayAllObjects = []

# The current object being read

sayAllObjectIndex = 0

# The number of objects to speak

sayAllObjectCount = 0

# The object representing the root of the currently active page

activePage = None

# Advance to the next hypertext object in the say all list and speak it

def presentNextHypertext():
    global sayAllObjectIndex
    global sayAllObjectIndex

    start = 0
    end = 0

    # Find the next object with text

    text = ""
    while text == "" and sayAllObjectIndex < sayAllObjectCount:
        obj = sayAllObjects[sayAllObjectIndex]
        sayAllObjectIndex = sayAllObjectIndex + 1
        txt = obj.text
        if txt is None:

            # If it's an image, read the image's name using the image voice

            text = obj.name
            if obj.role == rolenames.ROLE_IMAGE:

                # If we're getting the file name of the image, don't read it

                if text.find(".gif") >= 0 or \
                       text.find(".gif") >= 0 or \
                       text.find(".jpg") >= 0:
                    text = ""
                    sayAllObjectIndex = sayAllObjectIndex + 1
                    continue
                else:
                    speech.speak(text, "image")
            elif text is not "":
                speech.speak(text)
            if text == "":
                sayAllObjectIndex = sayAllObjectIndex + 1
                continue
            else:

                # Stop looking for more objects, we're speaking one now

                break

        # Get the entire contents of this hypertext object

        text = txt.getText(0, -1)

        # Get the hypertext interface to this object

        ht = obj.hypertext
        if ht is None:
            nLinks = 0
        else:
            nLinks = ht.getNLinks()
        if nLinks == 0:
            speech.speak(text)

        # Speak this hypertext object in chunks

        else:

            # Split up the links

            position = 0
            i = 0
            while i < nLinks:
                hl = ht.getLink(i)

                # We don't get proper start and end offsets, so hack
                # hack hack

                # Get the text of the hyperlink

                anchor = hl.getObject(0)
                name = anchor.name
                start = text[position:].find(name)
                if start == -1:
                    break
                start = start+position
                end = start+len(name)
    
                # If there is text between where we are now and the beginning of the link, read it first

                if start != position:
                    speech.speak(text[position:start])

                # Speak the text of the hyperlink using the hyperlink voice

                speech.speak(text[start:end], "hyperlink")
                position = end
                i = i + 1

            # We're done speaking the hyperlinks - if there's text
            # left, spaek it

            if end < len(text):
                speech.speak(text[end:])

    # If we have no more objects to speak, end say all mode

    if sayAllObjectIndex == sayAllObjectCount:
        return False
    else:
        return True
    

# This function is called by say all mode when another chunk of text
# is needed

def getChunk():
    global sayAllObjects
    global sayAllObjectIndex
    global sayAllObjectCount

    return presentNextHypertext()

# This function is called when say all mode is finished - it currently
# does nothing

def sayAllDone(position):
    pass


