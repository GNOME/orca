#!/usr/bin/python

"""Test of HTML combo box output of Firefox, including label guess and
forcing a combo box that has been reached by caret browsing to expand
and gain focus.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on a blank Firefox window.
#
sequence.append(WaitForWindowActivate(utils.firefoxFrameNames, None))

########################################################################
# Load the local combo box test case.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_ENTRY))

sequence.append(TypeAction(utils.htmlURLPrefix + "combobox.html"))
sequence.append(KeyComboAction("Return"))

sequence.append(WaitForDocLoad())
sequence.append(WaitForFocus("Combo Box Regression Test",
                             acc_role=pyatspi.ROLE_DOCUMENT_FRAME))

########################################################################
# Press Control+Home to move to the top.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "Top of file", 
    ["BRAILLE LINE:  'Severity: Severity normal Combo'",
     "     VISIBLE:  'Severity: Severity normal Combo', cursor=1",
     "SPEECH OUTPUT: 'Severity link : Severity normal combo box'"]))

########################################################################
# Press Tab once to get to the Severity link. 
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "Tab to Severity combo box", 
    ["BRAILLE LINE:  'Severity: Severity normal Combo'",
     "     VISIBLE:  'Severity: Severity normal Combo', cursor=1",
     "SPEECH OUTPUT: 'Severity link'"]))

########################################################################
# Read the current line with KP_8.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_8", 1000))
sequence.append(utils.AssertPresentationAction(
    "flat review current line", 
    ["BRAILLE LINE:  'Severity Severity :  normal $l'",
     "     VISIBLE:  'Severity Severity :  normal $l', cursor=10",
     "SPEECH OUTPUT: 'Severity Severity :  normal'"]))

########################################################################
# Read the rest of the document with KP_9.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_9"))
sequence.append(utils.AssertPresentationAction(
    "flat review next line", 
    ["BRAILLE LINE:  'Priority :  Normal $l'",
     "     VISIBLE:  'Priority :  Normal $l', cursor=1",
     "SPEECH OUTPUT: 'Priority :  Normal'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_9"))
sequence.append(utils.AssertPresentationAction(
    "flat review next line", 
    ["BRAILLE LINE:  'Resolution:  $l'",
     "     VISIBLE:  'Resolution:  $l', cursor=1",
     "SPEECH OUTPUT: 'Resolution: ",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_9"))
sequence.append(utils.AssertPresentationAction(
    "flat review next line", 
    ["BRAILLE LINE:  'FIXED $l'",
     "     VISIBLE:  'FIXED $l', cursor=1",
     "SPEECH OUTPUT: 'FIXED' voice=uppercase"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_9"))
sequence.append(utils.AssertPresentationAction(
    "flat review next line", 
    ["BRAILLE LINE:  'Version 2.16 $l'",
     "     VISIBLE:  'Version 2.16 $l', cursor=1",
     "SPEECH OUTPUT: 'Version 2.16'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_9"))
sequence.append(utils.AssertPresentationAction(
    "flat review next line", 
    ["BRAILLE LINE:  'Component $l'",
     "     VISIBLE:  'Component $l', cursor=1",
     "SPEECH OUTPUT: 'Component'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_9"))
sequence.append(utils.AssertPresentationAction(
    "flat review next line", 
    ["BRAILLE LINE:  'Speech $l'",
     "     VISIBLE:  'Speech $l', cursor=1",
     "SPEECH OUTPUT: 'Speech'"]))

########################################################################
# Move to the location bar by pressing Control+L.  When it has focus
# type "about:blank" and press Return to restore the browser to the
# conditions at the test's start.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_ENTRY))

sequence.append(TypeAction("about:blank"))
sequence.append(KeyComboAction("Return"))

sequence.append(WaitForDocLoad())

# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(3000))

sequence.append(utils.AssertionSummaryAction())

sequence.start()
