# -*- coding: utf-8 -*-
#!/usr/bin/python

"""Test of HTML links output of Firefox, in particular structural
navigation.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on a blank Firefox window.
#
sequence.append(WaitForWindowActivate("Minefield",None))

########################################################################
# Load the local links test case.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus("Location", acc_role=pyatspi.ROLE_ENTRY))

sequence.append(TypeAction(utils.htmlURLPrefix + "anchors2.html"))
sequence.append(KeyComboAction("Return"))

sequence.append(WaitForDocLoad())
sequence.append(WaitForFocus("Links to test files",
                             acc_role=pyatspi.ROLE_DOCUMENT_FRAME))

########################################################################
# Press Control+Home to move to the top.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "Top of file", 
    ["BRAILLE LINE:  'Here are some of our local test files:'",
     "     VISIBLE:  'Here are some of our local test ', cursor=1",
     "SPEECH OUTPUT: 'Here are some of our local test files:'"]))

########################################################################
# Press U to move to the next unvisited link, anchors.html. Note that 
# for the braille I have replaced the bullet character with an asterisk
# as the bullets are causing "Non-ASCII character" syntax errors.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("u"))
sequence.append(utils.AssertPresentationAction(
    "u to anchors.html link", 
    ["BRAILLE LINE:  '• anchors.html Link'",
     "     VISIBLE:  '• anchors.html Link', cursor=3",
     "SPEECH OUTPUT: 'anchors.html link'"]))

########################################################################
# Press U to move to the next unvisited link, blockquotes.html
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("u"))
sequence.append(utils.AssertPresentationAction(
    "u to blockquotes.html link", 
    ["BRAILLE LINE:  '• blockquotes.html Link'",
     "     VISIBLE:  '• blockquotes.html Link', cursor=3",
     "SPEECH OUTPUT: 'blockquotes.html link'"]))

########################################################################
# Press Shift+U to move to the previous unvisited link.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>u"))
sequence.append(utils.AssertPresentationAction(
    "shift + u to anchors.html link", 
    ["BRAILLE LINE:  '• anchors.html Link'",
     "     VISIBLE:  '• anchors.html Link', cursor=3",
     "SPEECH OUTPUT: 'anchors.html link'"]))

########################################################################
# Press Shift+U to move to the previous unvisited link.  Note that there
# are no more previous links between us and the top of the page. 
# Therefore we wrap to the bottom (and announce that fact) and then 
# move to the first link we come to.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>u"))
sequence.append(utils.AssertPresentationAction(
    "shift + u wrapping to bottom",
    ["BRAILLE LINE:  '• textattributes.html Link'",
     "     VISIBLE:  '• textattributes.html Link', cursor=3",
     "SPEECH OUTPUT: 'Wrapping to bottom.'",
     "SPEECH OUTPUT: 'textattributes.html link'"])) 

########################################################################
# Press Shift+U to move to the previous unvisited link.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>u"))
sequence.append(utils.AssertPresentationAction(
    "shift + u to tables.html",
    ["BRAILLE LINE:  '• tables.html Link'",
     "     VISIBLE:  '• tables.html Link', cursor=3",
     "SPEECH OUTPUT: 'tables.html link'"])) 

########################################################################
# Press Return to follow the tables.html link.
#
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForDocLoad())

########################################################################
# Press Alt+Left Arrow to return to the anchors2.html page.
#
sequence.append(KeyComboAction("<Alt>Left"))
sequence.append(WaitForDocLoad())

########################################################################
# Press U to move to the next unvisited link, anchors.html. 
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("u"))
sequence.append(utils.AssertPresentationAction(
    "u to anchors.html link", 
    ["BRAILLE LINE:  '• anchors.html Link'",
     "     VISIBLE:  '• anchors.html Link', cursor=3",
     "SPEECH OUTPUT: 'anchors.html link'"]))

########################################################################
# Press U to move to the next unvisited link, blockquotes.html
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("u"))
sequence.append(utils.AssertPresentationAction(
    "u to blockquotes.html link", 
    ["BRAILLE LINE:  '• blockquotes.html Link'",
     "     VISIBLE:  '• blockquotes.html Link', cursor=3",
     "SPEECH OUTPUT: 'blockquotes.html link'"]))

########################################################################
# Press Return to follow the blockquotes.html link.
#
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForDocLoad())

########################################################################
# Press Alt+Left Arrow to return to the anchors2.html page.
#
sequence.append(KeyComboAction("<Alt>Left"))
sequence.append(WaitForDocLoad())

########################################################################
# Press V to move to the next visited link, blockquotes.html. 
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("v"))
sequence.append(utils.AssertPresentationAction(
    "v to blockquotes.html link", 
    ["BRAILLE LINE:  '• blockquotes.html Link'",
     "     VISIBLE:  '• blockquotes.html Link', cursor=3",
     "SPEECH OUTPUT: 'blockquotes.html link'"]))

########################################################################
# Press V to move to the next visited link, tables.html
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("v"))
sequence.append(utils.AssertPresentationAction(
    "v to tables.html link", 
    ["BRAILLE LINE:  '• tables.html Link'",
     "     VISIBLE:  '• tables.html Link', cursor=3",
     "SPEECH OUTPUT: 'tables.html link'"]))

########################################################################
# Press V to move to the next visited link, blockquotes.html 
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("v"))
sequence.append(utils.AssertPresentationAction(
    "v to blockquotes.html link", 
    ["BRAILLE LINE:  '• blockquotes.html Link'",
     "     VISIBLE:  '• blockquotes.html Link', cursor=3",
     "SPEECH OUTPUT: 'Wrapping to top.'",
     "SPEECH OUTPUT: 'blockquotes.html link'"]))

########################################################################
# Press Shift V to move to the previous visited link, tables.html. 
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>v"))
sequence.append(utils.AssertPresentationAction(
    "shift + v to tables.html link", 
    ["BRAILLE LINE:  '• tables.html Link'",
     "     VISIBLE:  '• tables.html Link', cursor=3",
     "SPEECH OUTPUT: 'Wrapping to bottom.'",
     "SPEECH OUTPUT: 'tables.html link'"]))

########################################################################
# Move to the location bar by pressing Control+L.  When it has focus
# type "about:blank" and press Return to restore the browser to the
# conditions at the test's start.
#
sequence.append(KeyComboAction("<Control>l", 1000))
sequence.append(WaitForFocus("Location", acc_role=pyatspi.ROLE_ENTRY))

sequence.append(TypeAction("about:blank"))
sequence.append(KeyComboAction("Return"))

sequence.append(WaitForDocLoad())

# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(3000))

sequence.append(utils.AssertionSummaryAction())

sequence.start()
