# -*- coding: utf-8 -*-
#!/usr/bin/python

"""Test of Where am I for HTML links in Firefox
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

sequence.append(TypeAction(utils.htmlURLPrefix + "bugzilla_top.html"))
sequence.append(KeyComboAction("Return"))

sequence.append(WaitForDocLoad())
sequence.append(WaitForFocus("GNOME Bug Tracking System",
                             acc_role=pyatspi.ROLE_DOCUMENT_FRAME))

########################################################################
# Shift+Tab to Product summary link and do a Where Am I
#
sequence.append(KeyComboAction("<Shift>Tab"))
sequence.append(WaitForFocus("Product summary", acc_role=pyatspi.ROLE_LINK))
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Where Am I on Product summary link", 
    ["BRAILLE LINE:  '3.Product summary (designed for maintainers)'",
     "     VISIBLE:  'Product summary (designed for ma', cursor=1",
     "SPEECH OUTPUT: 'http link Product summary different site'"]))

########################################################################
# Go home tab and do a Where Am I
#
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(WaitForFocus("Home", acc_role=pyatspi.ROLE_LINK))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("New bug", acc_role=pyatspi.ROLE_LINK))
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Where Am I on New bug link", 
    ["BRAILLE LINE:  'New bug · Browse · Search · Reports · Account · Admin · Help'",
     "     VISIBLE:  'New bug · Browse · Search · Repo', cursor=1",
     "SPEECH OUTPUT: 'http link New bug different site'"]))

########################################################################
# Shift+Tab back to the footprint
#
sequence.append(KeyComboAction("<Shift>Tab"))
sequence.append(WaitForFocus("Home", acc_role=pyatspi.ROLE_LINK))
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Where Am I on footprint", 
    ["BUG? - Is it redundant to speak link twice?",
     "BRAILLE LINE:  'Home Image'",
     "     VISIBLE:  'Home Image', cursor=1",
     "SPEECH OUTPUT: 'http link Home link image different site'"]))

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
