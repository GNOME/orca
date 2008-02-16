#!/usr/bin/python

"""Test of UIUC radio button presentation using Firefox.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on the Firefox window as well as for focus
# to move to the "inline: Radio Example 1" frame.
#
sequence.append(WaitForWindowActivate("Minefield",None))

########################################################################
# Load the UIUC button demo.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus("Location", acc_role=pyatspi.ROLE_ENTRY))
sequence.append(TypeAction("http://test.cita.uiuc.edu/aria/radio/view_inline.php?title=Radio%20Example%201&ginc=includes/radio1_inline.inc&gcss=css/radio1_inline.css&gjs=../js/globals.js,../js/widgets_inline.js,js/radio1_inline.js"))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForDocLoad())
sequence.append(WaitForFocus("inline: Radio Example 1", acc_role=pyatspi.ROLE_DOCUMENT_FRAME))

########################################################################
# Move to the first radio button.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "tab to first button again", 
    ["BRAILLE LINE:  '& y Thai RadioButton'",
     "     VISIBLE:  '& y Thai RadioButton', cursor=1",
     "BRAILLE LINE:  '& y Thai RadioButton'",
     "     VISIBLE:  '& y Thai RadioButton', cursor=1",
     "SPEECH OUTPUT: 'Lunch Options panel'",
     "SPEECH OUTPUT: 'Thai not selected radio button'"]))
########################################################################
# Do a basic "Where Am I" via KP_Enter.  The following should be
# presented in speech and braille:
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "basic whereamI", 
    ["BRAILLE LINE:  '& y Thai RadioButton'",
     "     VISIBLE:  '& y Thai RadioButton', cursor=1",
     "SPEECH OUTPUT: 'Lunch Options'",
     "SPEECH OUTPUT: 'Thai radio button'",
     "SPEECH OUTPUT: 'not selected'",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: ''"]))
########################################################################
# Move to the second radio button.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "move to second radio button", 
    ["BRAILLE LINE:  '&=y Subway RadioButton'",
     "     VISIBLE:  '&=y Subway RadioButton', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Subway selected radio button'"]))

########################################################################
# Move to the third radio button.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "move to third radio button", 
    ["BRAILLE LINE:  '&=y Jimmy Johns RadioButton'",
     "     VISIBLE:  '&=y Jimmy Johns RadioButton', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Jimmy Johns selected radio button'"]))
########################################################################
# Move to the fourth radio button.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "move to fourth radio button", 
    ["BRAILLE LINE:  '&=y Radio Maria RadioButton'",
     "     VISIBLE:  '&=y Radio Maria RadioButton', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Radio Maria selected radio button'"]))
########################################################################
# Move to the fifth radio button.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "move to fifth radio button", 
    ["BRAILLE LINE:  '&=y Rainbow Gardens RadioButton'",
     "     VISIBLE:  '&=y Rainbow Gardens RadioButton', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Rainbow Gardens selected radio button'"]))
########################################################################
# Move to the second radio button group (panel).  Contrast to the first group
# where the "Water" radio button already has been selected.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "tab to second radio group", 
    ["BRAILLE LINE:  '&=y Water RadioButton'",
     "     VISIBLE:  '&=y Water RadioButton', cursor=1",
     "BRAILLE LINE:  '&=y Water RadioButton'",
     "     VISIBLE:  '&=y Water RadioButton', cursor=1",
     "SPEECH OUTPUT: 'Drink Options panel'",
     "SPEECH OUTPUT: 'Water selected radio button'"]))
########################################################################
# Move to the second radio button.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "move to second radio button grp2", 
    ["BRAILLE LINE:  '&=y Tea RadioButton'",
     "     VISIBLE:  '&=y Tea RadioButton', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Tea selected radio button'"]))
########################################################################
# Move back to the first radio button.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "move back to first radio button grp2", 
    ["BRAILLE LINE:  '&=y Water RadioButton'",
     "     VISIBLE:  '&=y Water RadioButton', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Water selected radio button'"]))
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
