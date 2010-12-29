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
sequence.append(WaitForWindowActivate(utils.firefoxFrameNames, None))

########################################################################
# Load the UIUC button demo.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_ENTRY))
sequence.append(TypeAction("http://test.cita.illinois.edu/aria/button/button1.php"))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForDocLoad())
sequence.append(WaitForFocus("class: Button Example 1", acc_role=pyatspi.ROLE_DOCUMENT_FRAME))

sequence.append(PauseAction(6000))

########################################################################
# Tab to the first button.  The following will be presented.
#
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("Tab"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "tab to first button", 
    ["BRAILLE LINE:  '& y Font Larger + ToggleButton & y Font Smaller - ToggleButton &=y Italic i ToggleButton & y Bold B ToggleButton'",
     "     VISIBLE:  '& y Font Larger + ToggleButton &', cursor=1",
     "SPEECH OUTPUT: 'Text Formating Controls 1 list Font Larger + toggle button not pressed'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  The following should be
# presented in speech and braille:
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "basic whereamI", 
    ["BRAILLE LINE:  '& y Font Larger + ToggleButton & y Font Smaller - ToggleButton &=y Italic i ToggleButton & y Bold B ToggleButton'",
     "     VISIBLE:  '& y Font Larger + ToggleButton &', cursor=1",
     "SPEECH OUTPUT: 'Font Larger + toggle button not pressed'"]))

########################################################################
# Tab to the second button.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "tab to second button", 
    ["BRAILLE LINE:  '& y Font Larger + ToggleButton & y Font Smaller - ToggleButton &=y Italic i ToggleButton & y Bold B ToggleButton'",
     "     VISIBLE:  '& y Font Smaller - ToggleButton ', cursor=1",
     "SPEECH OUTPUT: 'Font Smaller - toggle button not pressed'"]))

########################################################################
# Now push the second button.  The following will be presented.
#
sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction(" "))
sequence.append(utils.AssertPresentationAction(
    "push second button", 
    ["BRAILLE LINE:  '& y Font Larger + ToggleButton & y Font Smaller - ToggleButton &=y Italic i ToggleButton & y Bold B ToggleButton'",
     "     VISIBLE:  '& y Font Smaller - ToggleButton ', cursor=1",
     "SPEECH OUTPUT: 'not pressed'"]))

########################################################################
# Tab to the third button.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "tab to third button", 
    ["BRAILLE LINE:  '& y Font Larger + ToggleButton & y Font Smaller - ToggleButton &=y Italic i ToggleButton & y Bold B ToggleButton'",
     "     VISIBLE:  '&=y Italic i ToggleButton & y Bo', cursor=1",
     "SPEECH OUTPUT: 'Italic i toggle button pressed'"]))

########################################################################
# Now push the third button.  The following will be presented.
#
sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction(" "))
sequence.append(utils.AssertPresentationAction(
    "push third button", 
    ["BRAILLE LINE:  '& y Font Larger + ToggleButton & y Font Smaller - ToggleButton & y Italic i ToggleButton & y Bold B ToggleButton'",
     "     VISIBLE:  '& y Italic i ToggleButton & y Bo', cursor=1",
     "SPEECH OUTPUT: 'not pressed'"]))

########################################################################
# Tab to the fourth button.  The following will be presented.
#
sequence.append(PauseAction(3000))
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "tab to fourth button", 
    ["BRAILLE LINE:  '& y Font Larger + ToggleButton & y Font Smaller - ToggleButton & y Italic i ToggleButton & y Bold B ToggleButton'",
     "     VISIBLE:  '& y Bold B ToggleButton', cursor=1",
     "SPEECH OUTPUT: 'Bold B toggle button not pressed'"]))

########################################################################
# Now push the fourth button.  The following will be presented.
#
sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction("  "))
sequence.append(utils.AssertPresentationAction(
    "push fourth button", 
    ["BUG? - Toggling doesn't appear to be working right here or on the next attempt.",
     "BRAILLE LINE:  '& y Font Larger + ToggleButton & y Font Smaller - ToggleButton & y Italic i ToggleButton &=y Bold B ToggleButton'",
     "     VISIBLE:  '&=y Bold B ToggleButton', cursor=1",
     "BRAILLE LINE:  '& y Font Larger + ToggleButton & y Font Smaller - ToggleButton & y Italic i ToggleButton & y Bold B ToggleButton'",
     "     VISIBLE:  '& y Bold B ToggleButton', cursor=1",
     "SPEECH OUTPUT: 'pressed'",
     "SPEECH OUTPUT: 'not pressed'"]))

########################################################################
# Now push the fourth button again.  The following will be presented.
#
sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction("  "))
sequence.append(utils.AssertPresentationAction(
    "push fourth button again", 
    ["BRAILLE LINE:  '& y Font Larger + ToggleButton & y Font Smaller - ToggleButton & y Italic i ToggleButton &=y Bold B ToggleButton'",
     "     VISIBLE:  '&=y Bold B ToggleButton', cursor=1",
     "BRAILLE LINE:  '& y Font Larger + ToggleButton & y Font Smaller - ToggleButton & y Italic i ToggleButton & y Bold B ToggleButton'",
     "     VISIBLE:  '& y Bold B ToggleButton', cursor=1",
     "SPEECH OUTPUT: 'pressed'",
     "SPEECH OUTPUT: 'not pressed'"]))

########################################################################
# Close the demo
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
