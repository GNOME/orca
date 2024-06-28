#!/usr/bin/python

"""Test of Dojo checkbox presentation."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

#sequence.append(WaitForDocLoad())
sequence.append(PauseAction(5000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "1. Tab to the cb0 checkbox",
    ["KNOWN ISSUE: We are not presenting this in Nightly; we do with stable",
     "BRAILLE LINE:  '<x> cb0: Vanilla (non-dojo) checkbox (for comparison purposes) check box'",
     "     VISIBLE:  '<x> cb0: Vanilla (non-dojo) chec', cursor=1",
     "SPEECH OUTPUT: 'form'",
     "SPEECH OUTPUT: 'cb0: Vanilla (non-dojo) checkbox (for comparison purposes) check box checked.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction(" "))
sequence.append(utils.AssertPresentationAction(
    "2. Change state on cb0 checkbox",
    ["BRAILLE LINE:  '< > cb0: Vanilla (non-dojo) checkbox (for comparison purposes) check box'",
     "     VISIBLE:  '< > cb0: Vanilla (non-dojo) chec', cursor=1",
     "SPEECH OUTPUT: 'not checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "3. Tab to the cb1 checkbox",
    ["BRAILLE LINE:  '< > cb1: normal checkbox, with value=foo, clicking generates console log messages check box'",
     "     VISIBLE:  '< > cb1: normal checkbox, with v', cursor=1",
     "SPEECH OUTPUT: 'cb1: normal checkbox, with value=foo, clicking generates console log messages check box not checked.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction(" "))
sequence.append(utils.AssertPresentationAction(
    "4. Change state on cb1 checkbox",
    ["BRAILLE LINE:  '<x> cb1: normal checkbox, with value=foo, clicking generates console log messages check box'",
     "     VISIBLE:  '<x> cb1: normal checkbox, with v', cursor=1",
     "SPEECH OUTPUT: 'checked'"]))

sequence.append(KeyComboAction("Tab"))
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "5. Tab to the cb2 checkbox",
    ["BRAILLE LINE:  '<x> cb2: normal checkbox, with default value, initially turned on. check box'",
     "     VISIBLE:  '<x> cb2: normal checkbox, with d', cursor=1",
     "SPEECH OUTPUT: 'cb2: normal checkbox, with default value, initially turned on. check box checked.'"]))

sequence.append(KeyComboAction("Tab"))
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "6. Tab to the cb4 checkbox",
    ["BRAILLE LINE:  '<x> cb4: readOnly checkbox, turned on check box'",
     "     VISIBLE:  '<x> cb4: readOnly checkbox, turn', cursor=1",
     "SPEECH OUTPUT: 'cb4: readOnly checkbox, turned on check box checked.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "7. Tab to the cb5 checkbox",
    ["BRAILLE LINE:  '< > cb5: normal checkbox, with specified value=\"\", clicking generates console log messages check box'",
     "     VISIBLE:  '< > cb5: normal checkbox, with s', cursor=1",
     "SPEECH OUTPUT: 'cb5: normal checkbox, with specified value=\"\", clicking generates console log messages check box not checked.'"]))

sequence.append(KeyComboAction("Tab"))
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "8. Tab to the cb6 checkbox",
    ["BRAILLE LINE:  '<x> cb6: instantiated from script check box'",
     "     VISIBLE:  '<x> cb6: instantiated from scrip', cursor=1",
     "SPEECH OUTPUT: 'cb6: instantiated from script check box checked.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "9. Tab to the cb7 checkbox",
    ["BRAILLE LINE:  '< > cb7: normal checkbox. check box'",
     "     VISIBLE:  '< > cb7: normal checkbox. check ', cursor=1",
     "SPEECH OUTPUT: 'cb7: normal checkbox. check box not checked.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "10. Basic Where Am I",
    ["BRAILLE LINE:  '< > cb7: normal checkbox. check box'",
     "     VISIBLE:  '< > cb7: normal checkbox. check ', cursor=1",
     "SPEECH OUTPUT: 'cb7: normal checkbox. check box not checked.'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
