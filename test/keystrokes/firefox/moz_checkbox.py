#!/usr/bin/python

"""Test of Mozilla ARIA checkbox presentation using Firefox.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on the Firefox window as well as for focus
# to move to the "DHTML Checkbox" frame.
#
sequence.append(WaitForWindowActivate(utils.firefoxFrameNames, None))

########################################################################
# Load the Mozilla ARIA checkbox demo.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_ENTRY))
sequence.append(TypeAction("http://www.mozilla.org/access/dhtml/checkbox"))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForDocLoad())
sequence.append(WaitForFocus("ARIA Checkbox", acc_role=pyatspi.ROLE_DOCUMENT_FRAME))

########################################################################
# Tab to the first checkbox.
# [[[Bug?: repeated Braille.  below are expected results]]]
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "tab to first checkbox", 
    ["BRAILLE LINE:  '<x> Include decorative fruit basket CheckBox'",
     "     VISIBLE:  '<x> Include decorative fruit bas', cursor=1",
     "SPEECH OUTPUT: 'Include decorative fruit basket check box checked'"]))

########################################################################
# Now, change its state.
#
sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction(" "))
sequence.append(utils.AssertPresentationAction(
    "change state of first checkbox", 
    ["BRAILLE LINE:  '< > Include decorative fruit basket CheckBox'",
     "     VISIBLE:  '< > Include decorative fruit bas', cursor=1",
     "SPEECH OUTPUT: 'not checked'"]))

########################################################################
# Tab to the second checkbox.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "tab to second checkbox", 
    ["BRAILLE LINE:  '<x> Invalid checkbox CheckBox'",
     "     VISIBLE:  '<x> Invalid checkbox CheckBox', cursor=1",
     "SPEECH OUTPUT: 'Invalid checkbox check box checked'"]))

########################################################################
# Now, change its state.
#
sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction(" "))
sequence.append(utils.AssertPresentationAction(
    "change state of second checkbox", 
    ["BRAILLE LINE:  '< > Invalid checkbox CheckBox'",
     "     VISIBLE:  '< > Invalid checkbox CheckBox', cursor=1",
     "SPEECH OUTPUT: 'not checked'"]))

########################################################################
# Tab to the third checkbox.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "tab to third checkbox", 
    ["BRAILLE LINE:  '<x> Required checkbox CheckBox'",
     "     VISIBLE:  '<x> Required checkbox CheckBox', cursor=1",
     "SPEECH OUTPUT: 'Required checkbox check box checked required'"]))
    
########################################################################
# Now, change its state.
#
sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction(" "))
sequence.append(utils.AssertPresentationAction(
    "change state of third checkbox", 
    ["BRAILLE LINE:  '< > Required checkbox CheckBox'",
     "     VISIBLE:  '< > Required checkbox CheckBox', cursor=1",
     "SPEECH OUTPUT: 'not checked'"]))

########################################################################
# Now, change its state back.
#
sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction(" "))
sequence.append(utils.AssertPresentationAction(
    "change state of third checkbox again", 
    ["BRAILLE LINE:  '<x> Required checkbox CheckBox'",
     "     VISIBLE:  '<x> Required checkbox CheckBox', cursor=1",
     "SPEECH OUTPUT: 'checked'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "basic whereAmI", 
    ["BRAILLE LINE:  '<x> Required checkbox CheckBox'",
     "     VISIBLE:  '<x> Required checkbox CheckBox', cursor=1",
     "SPEECH OUTPUT: 'Required checkbox check box checked"]))
     
########################################################################
# Tab to the checkbox tristate.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "tab to checkbox tristate", 
    ["BRAILLE LINE:  '<x> Tri-state checkbox CheckBox'",
     "     VISIBLE:  '<x> Tri-state checkbox CheckBox', cursor=1",
     "SPEECH OUTPUT: 'Tri-state checkbox check box checked required'"]))
    
########################################################################
# change checkbox tristate state three times
#
sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction(" "))
sequence.append(utils.AssertPresentationAction(
    "1 change state of tristate checkbox", 
    ["BRAILLE LINE:  '< > Tri-state checkbox CheckBox'",
     "     VISIBLE:  '< > Tri-state checkbox CheckBox', cursor=1",
     "SPEECH OUTPUT: 'not checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction(" "))
sequence.append(utils.AssertPresentationAction(
    "2 change state of tristate checkbox", 
    ["BRAILLE LINE:  '<-> Tri-state checkbox CheckBox'",
     "     VISIBLE:  '<-> Tri-state checkbox CheckBox', cursor=1",
     "SPEECH OUTPUT: 'partially checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction(" "))
sequence.append(utils.AssertPresentationAction(
    "3 change state of tristate checkbox", 
    ["BRAILLE LINE:  '<x> Tri-state checkbox CheckBox'",
     "     VISIBLE:  '<x> Tri-state checkbox CheckBox', cursor=1",
     "SPEECH OUTPUT: 'checked'"]))

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
