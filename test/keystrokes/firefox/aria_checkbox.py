#!/usr/bin/python

"""Test of ARIA checkbox presentation."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "1. Tab to first checkbox",
    ["KNOWN ISSUE: The indicators are all missing",
     "BRAILLE LINE:  ' Include decorative fruit basket'",
     "     VISIBLE:  ' Include decorative fruit basket', cursor=1",
     "BRAILLE LINE:  ' Include decorative fruit basket'",
     "     VISIBLE:  ' Include decorative fruit basket', cursor=1",
     "SPEECH OUTPUT: 'Include decorative fruit basket check box checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction(" "))
sequence.append(utils.AssertPresentationAction(
    "2. Change state of first checkbox",
    ["BRAILLE LINE:  ' Include decorative fruit basket'",
     "     VISIBLE:  ' Include decorative fruit basket', cursor=1",
     "SPEECH OUTPUT: 'not checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "3. Tab to second checkbox",
    ["BRAILLE LINE:  ' Invalid checkbox'",
     "     VISIBLE:  ' Invalid checkbox', cursor=1",
     "BRAILLE LINE:  ' Invalid checkbox'",
     "     VISIBLE:  ' Invalid checkbox', cursor=1",
     "SPEECH OUTPUT: 'Invalid checkbox check box checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction(" "))
sequence.append(utils.AssertPresentationAction(
    "4. Change state of second checkbox",
    ["BRAILLE LINE:  ' Invalid checkbox'",
     "     VISIBLE:  ' Invalid checkbox', cursor=1",
     "SPEECH OUTPUT: 'not checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "5. Tab to third checkbox",
    ["BRAILLE LINE:  ' Required checkbox'",
     "     VISIBLE:  ' Required checkbox', cursor=1",
     "BRAILLE LINE:  ' Required checkbox'",
     "     VISIBLE:  ' Required checkbox', cursor=1",
     "SPEECH OUTPUT: 'Required checkbox check box checked required'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction(" "))
sequence.append(utils.AssertPresentationAction(
    "6. Change state of third checkbox",
    ["BRAILLE LINE:  ' Required checkbox'",
     "     VISIBLE:  ' Required checkbox', cursor=1",
     "SPEECH OUTPUT: 'not checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction(" "))
sequence.append(utils.AssertPresentationAction(
    "7. Change state of third checkbox again",
    ["BRAILLE LINE:  ' Required checkbox'",
     "     VISIBLE:  ' Required checkbox', cursor=1",
     "SPEECH OUTPUT: 'checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "8. Basic whereAmI",
    ["BRAILLE LINE:  ' Required checkbox'",
     "     VISIBLE:  ' Required checkbox', cursor=1",
     "SPEECH OUTPUT: 'Required checkbox'",
     "SPEECH OUTPUT: 'check box checked required'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "9. Tab to checkbox tristate",
    ["BRAILLE LINE:  ' Tri-state checkbox'",
     "     VISIBLE:  ' Tri-state checkbox', cursor=1",
     "BRAILLE LINE:  ' Tri-state checkbox'",
     "     VISIBLE:  ' Tri-state checkbox', cursor=1",
     "SPEECH OUTPUT: 'Tri-state checkbox check box checked required'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction(" "))
sequence.append(utils.AssertPresentationAction(
    "10. Change state of tristate checkbox",
    ["BRAILLE LINE:  ' Tri-state checkbox'",
     "     VISIBLE:  ' Tri-state checkbox', cursor=1",
     "SPEECH OUTPUT: 'not checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction(" "))
sequence.append(utils.AssertPresentationAction(
    "11. Change state of tristate checkbox",
    ["BRAILLE LINE:  ' Tri-state checkbox'",
     "     VISIBLE:  ' Tri-state checkbox', cursor=1",
     "SPEECH OUTPUT: 'partially checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction(" "))
sequence.append(utils.AssertPresentationAction(
    "12. Change state of tristate checkbox",
    ["BRAILLE LINE:  ' Tri-state checkbox'",
     "     VISIBLE:  ' Tri-state checkbox', cursor=1",
     "SPEECH OUTPUT: 'checked'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
