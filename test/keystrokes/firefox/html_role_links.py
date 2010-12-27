# -*- coding: utf-8 -*-
#!/usr/bin/python

"""Test of HTML links output of Firefox, including basic navigation and
where am I.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on a blank Firefox window.
#
sequence.append(WaitForWindowActivate(utils.firefoxFrameNames, None))

########################################################################
# Load the local anchors test case.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_ENTRY))

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
# Press Tab to move to the anchors.html link.  
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "Tab to anchors.html link", 
    ["BRAILLE LINE:  '•anchors.html'",
     "     VISIBLE:  '•anchors.html', cursor=2",
     "SPEECH OUTPUT: 'anchors.html link'"]))

########################################################################
# Press Tab to move to the blockquotes.html link.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "Tab to blockquotes.html link", 
    ["BRAILLE LINE:  '•blockquotes.html'",
     "     VISIBLE:  '•blockquotes.html', cursor=2",
     "SPEECH OUTPUT: 'blockquotes.html link'"]))

########################################################################
# Press Tab to move to the bugzilla_top.html link.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "Tab to bugzilla_top.html link", 
    ["BRAILLE LINE:  '•bugzilla_top.html'",
     "     VISIBLE:  '•bugzilla_top.html', cursor=2",
     "SPEECH OUTPUT: 'bugzilla_top.html link'"]))

########################################################################
# Press Shift+Tab to move to the blockquotes.html link.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>Tab"))
sequence.append(utils.AssertPresentationAction(
    "Shift Tab to blockquotes.html link", 
    ["BRAILLE LINE:  '•blockquotes.html'",
     "     VISIBLE:  '•blockquotes.html', cursor=2",
     "SPEECH OUTPUT: 'blockquotes.html link'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  Because we're on a link, we
# get special link-related information.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Basic Where Am I", 
    ["BRAILLE LINE:  '•blockquotes.html'",
     "     VISIBLE:  '•blockquotes.html', cursor=2",
     "SPEECH OUTPUT: 'file link to blockquotes.html same site 1188 bytes'"]))

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
sequence.append(PauseAction(3000))

# Hack to ignore a focus event that will temporarily update braille
#
sequence.append(KeyComboAction("Down"))
sequence.append(KeyComboAction("Up"))

########################################################################
# Press Up Arrow to move to the anchors.html link.  We probably won't
# get a focus event, so we'll just pause in the next step.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up to anchors.html", 
    ["BUG? - Focus is not leaving the link we were on. Probably one of those recent Gecko/Mozilla regressions. Need to investigate further.",
     "BRAILLE LINE:  '• anchors.html'",
     "     VISIBLE:  '• anchors.html', cursor=1",
     "SPEECH OUTPUT: '• anchors.html link'"]))

########################################################################
# Move to the location bar by pressing Control+L.  When it has focus
# type "about:blank" and press Return to restore the browser to the
# conditions at the test's start.
#
sequence.append(KeyComboAction("<Control>l", 1000))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_ENTRY))

sequence.append(TypeAction("about:blank"))
sequence.append(KeyComboAction("Return"))

sequence.append(WaitForDocLoad())

# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(3000))

sequence.append(utils.AssertionSummaryAction())

sequence.start()
