# -*- coding: utf-8 -*-
#!/usr/bin/python

"""Test of Dojo spinner presentation using Firefox.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on the Firefox window as well as for focus
# to move to the "Dojo Spinner Widget Test" frame.
#
sequence.append(WaitForWindowActivate(utils.firefoxFrameNames, None))

########################################################################
# Load the dojo spinner demo.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_ENTRY))
sequence.append(TypeAction(utils.DojoNightlyURLPrefix + "form/test_Spinner.html"))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForDocLoad())
sequence.append(WaitForFocus("Dojo Spinner Widget Test", acc_role=pyatspi.ROLE_DOCUMENT_FRAME))

########################################################################
# Give the widget a moment to construct itself.  Move to the top of
# the file because that seems to give us more consistent results for
# the first test.
#
sequence.append(PauseAction(3000))
sequence.append(KeyComboAction("<Control>Home"))

########################################################################
# Tab to the first spinner.  
# 
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "Tab to the first spinner",
    ["BRAILLE LINE:  '▲ ▼ Spinbox #1:  $l not fired yet! $lSet value to 400 Button Set value to null Button Set required to false Button'",
     "     VISIBLE:  'Spinbox #1:  $l not fired yet! $', cursor=13",
     "SPEECH OUTPUT: 'Spinbox #1: 900 selected spin button'"]))

########################################################################
# Use down arrow to decrement spinner value.  
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "first spinner decrement 1", 
    ["BUG? - Why aren't we speaking or displaying the new value??",
     "BRAILLE LINE:  '▲ ▼ Spinbox #1:  $l not fired yet! $lSet value to 400 Button Set value to null Button Set required to false Button'",
     "     VISIBLE:  'Spinbox #1:  $l not fired yet! $', cursor=13",
     "BRAILLE LINE:  '▲ ▼ Spinbox #1:  $l not fired yet! $lSet value to 400 Button Set value to null Button Set required to false Button'",
     "     VISIBLE:  'Spinbox #1:  $l not fired yet! $', cursor=13",
     "SPEECH OUTPUT: ''"]))

########################################################################
# Use down arrow to decrement spinner value.  
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "first spinner decrement 2", 
    ["BUG? - Why aren't we speaking or displaying the new value??",
     "BRAILLE LINE:  '▲ ▼ Spinbox #1:  $l not fired yet! $lSet value to 400 Button Set value to null Button Set required to false Button'",
     "     VISIBLE:  'Spinbox #1:  $l not fired yet! $', cursor=13",
     "BRAILLE LINE:  '▲ ▼ Spinbox #1:  $l not fired yet! $lSet value to 400 Button Set value to null Button Set required to false Button'",
     "     VISIBLE:  'Spinbox #1:  $l not fired yet! $', cursor=13",
     "SPEECH OUTPUT: ''"]))

########################################################################
# Use up arrow to increment spinner value. 
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "first spinner increment 1", 
    ["BUG? - Why aren't we speaking or displaying the new value??",
     "BRAILLE LINE:  '▲ ▼ Spinbox #1:  $l not fired yet! $lSet value to 400 Button Set value to null Button Set required to false Button'",
     "     VISIBLE:  'Spinbox #1:  $l not fired yet! $', cursor=13",
     "BRAILLE LINE:  '▲ ▼ Spinbox #1:  $l not fired yet! $lSet value to 400 Button Set value to null Button Set required to false Button'",
     "     VISIBLE:  'Spinbox #1:  $l not fired yet! $', cursor=13",
     "SPEECH OUTPUT: ''"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "basic whereAmI", 
    ["BUG? - Why aren't we displaying the current value??",
     "BRAILLE LINE:  '▲ ▼ Spinbox #1:  $l not fired yet! $lSet value to 400 Button Set value to null Button Set required to false Button'",
     "     VISIBLE:  'Spinbox #1:  $l not fired yet! $', cursor=13",
     "SPEECH OUTPUT: 'Spinbox #1: spin button 899'"]))

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
