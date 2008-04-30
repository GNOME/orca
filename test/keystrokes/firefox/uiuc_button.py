#!/usr/bin/python

"""Test of UIUC button presentation using Firefox.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on the Firefox window as well as for focus
# to move to the "text/html: Button Example 1" frame.
#
sequence.append(WaitForWindowActivate("Minefield",None))

########################################################################
# Load the UIUC button demo.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus("Location", acc_role=pyatspi.ROLE_ENTRY))
sequence.append(TypeAction("http://test.cita.uiuc.edu/aria/button/view_class.php?title=Button%20Example%201&ginc=includes/button1_class.inc&gcss=css/button1_class.css&gjs=../js/globals.js,../js/widgets_class.js,js/button1_class.js"))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForDocLoad())
sequence.append(WaitForFocus("class: Button Example 1", acc_role=pyatspi.ROLE_DOCUMENT_FRAME))

########################################################################
# Tab to the first button.  The following will be presented.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "tab to first button", 
    ["BRAILLE LINE:  'Font Larger + Button Font Smaller - Button & y Italic i ToggleButton Bold B Button'",
     "     VISIBLE:  'Font Larger + Button Font Smalle', cursor=1",
     "BRAILLE LINE:  'Font Larger + Button Font Smaller - Button & y Italic i ToggleButton Bold B Button'",
     "     VISIBLE:  'Font Larger + Button Font Smalle', cursor=1",
     "SPEECH OUTPUT: 'Text Formating Controls 1 list'",
     "SPEECH OUTPUT: 'Font Larger + button'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  The following should be
# presented in speech and braille:
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "basic whereamI", 
    ["BRAILLE LINE:  'Font Larger + Button Font Smaller - Button & y Italic i ToggleButton Bold B Button'",
     "     VISIBLE:  'Font Larger + Button Font Smalle', cursor=1",
     "SPEECH OUTPUT: 'Font Larger +'",
     "SPEECH OUTPUT: 'button'",
     "SPEECH OUTPUT: ''"]))

########################################################################
# Now push the first button.  The following will be presented.
#
#
sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction(" "))
sequence.append(utils.AssertPresentationAction(
    "push first button", 
    [""]))

########################################################################
# Tab to the second button.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "tab to second button", 
    ["BRAILLE LINE:  'Font Larger + Button Font Smaller - Button & y Italic i ToggleButton Bold B Button'",
     "     VISIBLE:  'Font Smaller - Button & y Italic', cursor=1",
     "BRAILLE LINE:  'Font Larger + Button Font Smaller - Button & y Italic i ToggleButton Bold B Button'",
     "     VISIBLE:  'Font Smaller - Button & y Italic', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Font Smaller - button'"]))

########################################################################
# Now push the second button.  The following will be presented.
#
sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction(" "))
sequence.append(utils.AssertPresentationAction(
    "push second button", 
    [""]))

########################################################################
# Tab to the third button.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "tab to third button", 
    ["BRAILLE LINE:  'Font Larger + Button Font Smaller - Button & y Italic i ToggleButton Bold B Button'",
     "     VISIBLE:  '& y Italic i ToggleButton Bold B', cursor=1",
     "BRAILLE LINE:  'Font Larger + Button Font Smaller - Button & y Italic i ToggleButton Bold B Button'",
     "     VISIBLE:  '& y Italic i ToggleButton Bold B', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Italic i toggle button not pressed'"]))

########################################################################
# Now push the third button.  The following will be presented.
#
sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction(" "))
sequence.append(utils.AssertPresentationAction(
    "push third button", 
    [""]))

########################################################################
# Tab to the fourth button.  The following will be presented.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "tab to fourth button", 
    ["BRAILLE LINE:  'Font Larger + Button Font Smaller - Button & y Italic i ToggleButton Bold B Button'",
     "     VISIBLE:  'Bold B Button', cursor=1",
     "BRAILLE LINE:  'Font Larger + Button Font Smaller - Button & y Italic i ToggleButton Bold B Button'",
     "     VISIBLE:  'Bold B Button', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Bold B button'"]))

########################################################################
# Now push the fourth button.  The following will be presented.
#
sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction           ("  "))
sequence.append(utils.AssertPresentationAction(
    "push fourth button", 
    [""]))

########################################################################
# Now push the fourth button again.  The following will be presented.
#
sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction           ("  "))
sequence.append(utils.AssertPresentationAction(
    "push fourth button again", 
    [""]))

########################################################################
# Close the demo
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus(acc_name="Location", acc_role=pyatspi.ROLE_ENTRY))
sequence.append(TypeAction("about:blank"))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForDocLoad())

# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(3000))

sequence.append(utils.AssertionSummaryAction())

sequence.start()
