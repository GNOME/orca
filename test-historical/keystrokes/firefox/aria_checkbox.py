#!/usr/bin/python

"""Test of ARIA checkbox presentation."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

#sequence.append(WaitForDocLoad())
sequence.append(PauseAction(5000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "1. Tab to first checkbox",
    ["BRAILLE LINE:  '<x> Include decorative fruit basket check box'",
     "     VISIBLE:  '<x> Include decorative fruit bas', cursor=1",
     "SPEECH OUTPUT: 'Include decorative fruit basket check box checked.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction(" "))
sequence.append(utils.AssertPresentationAction(
    "2. Change state of first checkbox",
    ["BRAILLE LINE:  '< > Include decorative fruit basket check box'",
     "     VISIBLE:  '< > Include decorative fruit bas', cursor=1",
     "SPEECH OUTPUT: 'not checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "3. Tab to second checkbox",
    ["BRAILLE LINE:  '<x> Invalid checkbox check box'",
     "     VISIBLE:  '<x> Invalid checkbox check box', cursor=1",
     "SPEECH OUTPUT: 'Invalid checkbox check box checked.'",
     "SPEECH OUTPUT: 'invalid entry'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction(" "))
sequence.append(utils.AssertPresentationAction(
    "4. Change state of second checkbox",
    ["BRAILLE LINE:  '< > Invalid checkbox check box'",
     "     VISIBLE:  '< > Invalid checkbox check box', cursor=1",
     "SPEECH OUTPUT: 'not checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "5. Tab to third checkbox",
    ["BRAILLE LINE:  '<x> Required checkbox check box'",
     "     VISIBLE:  '<x> Required checkbox check box', cursor=1",
     "SPEECH OUTPUT: 'Required checkbox check box checked required.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction(" "))
sequence.append(utils.AssertPresentationAction(
    "6. Change state of third checkbox",
    ["BRAILLE LINE:  '< > Required checkbox check box'",
     "     VISIBLE:  '< > Required checkbox check box', cursor=1",
     "SPEECH OUTPUT: 'not checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction(" "))
sequence.append(utils.AssertPresentationAction(
    "7. Change state of third checkbox again",
    ["BRAILLE LINE:  '<x> Required checkbox check box'",
     "     VISIBLE:  '<x> Required checkbox check box', cursor=1",
     "SPEECH OUTPUT: 'checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "8. Basic whereAmI",
    ["BRAILLE LINE:  '<x> Required checkbox check box'",
     "     VISIBLE:  '<x> Required checkbox check box', cursor=1",
     "SPEECH OUTPUT: 'Required checkbox check box checked required.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "9. Tab to checkbox tristate",
    ["BRAILLE LINE:  '<x> Tri-state checkbox check box'",
     "     VISIBLE:  '<x> Tri-state checkbox check box', cursor=1",
     "SPEECH OUTPUT: 'Tri-state checkbox check box checked required.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction(" "))
sequence.append(utils.AssertPresentationAction(
    "10. Change state of tristate checkbox",
    ["BRAILLE LINE:  '< > Tri-state checkbox check box'",
     "     VISIBLE:  '< > Tri-state checkbox check box', cursor=1",
     "SPEECH OUTPUT: 'not checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction(" "))
sequence.append(utils.AssertPresentationAction(
    "11. Change state of tristate checkbox",
    ["BRAILLE LINE:  '<-> Tri-state checkbox check box'",
     "     VISIBLE:  '<-> Tri-state checkbox check box', cursor=1",
     "SPEECH OUTPUT: 'partially checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction(" "))
sequence.append(utils.AssertPresentationAction(
    "12. Change state of tristate checkbox",
    ["BRAILLE LINE:  '<x> Tri-state checkbox check box'",
     "     VISIBLE:  '<x> Tri-state checkbox check box', cursor=1",
     "SPEECH OUTPUT: 'checked'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
