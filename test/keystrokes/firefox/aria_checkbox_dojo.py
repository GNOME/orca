#!/usr/bin/python

"""Test of Dojo checkbox presentation."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "1. Tab to the cb0 checkbox",
    ["BRAILLE LINE:  '<x> cb0: Vanilla (non-dojo) checkbox (for comparison purposes) check box '",
     "     VISIBLE:  '<x> cb0: Vanilla (non-dojo) chec', cursor=0",
     "SPEECH OUTPUT: 'cb0: Vanilla (non-dojo) checkbox (for comparison purposes) check box checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction(" "))
sequence.append(utils.AssertPresentationAction(
    "2. Change state on cb0 checkbox",
    ["BRAILLE LINE:  '< > cb0: Vanilla (non-dojo) checkbox (for comparison purposes) check box '",
     "     VISIBLE:  '< > cb0: Vanilla (non-dojo) chec', cursor=0",
     "SPEECH OUTPUT: 'not checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "3. Tab to the cb1 checkbox",
    ["BRAILLE LINE:  '< > cb1: normal checkbox, with value=foo, clicking generates console log messages check box  get('value') push button'",
     "     VISIBLE:  '< > cb1: normal checkbox, with v', cursor=0",
     "SPEECH OUTPUT: 'cb1: normal checkbox, with value=foo, clicking generates console log messages check box not checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction(" "))
sequence.append(utils.AssertPresentationAction(
    "4. Change state on cb1 checkbox",
    ["BRAILLE LINE:  '<x> cb1: normal checkbox, with value=foo, clicking generates console log messages check box  get('value') push button'",
     "     VISIBLE:  '<x> cb1: normal checkbox, with v', cursor=0",
     "SPEECH OUTPUT: 'checked'"]))

sequence.append(KeyComboAction("Tab"))
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "5. Tab to the cb2 checkbox",
    ["BRAILLE LINE:  '<x> cb2: normal checkbox, with default value, initially turned on. check box  \"onChange\" handler updates: [] get('value') push button'",
     "     VISIBLE:  '<x> cb2: normal checkbox, with d', cursor=0",
     "SPEECH OUTPUT: 'cb2: normal checkbox, with default value, initially turned on. check box checked'"]))

sequence.append(KeyComboAction("Tab"))
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "6. Tab to the cb4 checkbox",
    ["BRAILLE LINE:  '<x> cb4: readOnly checkbox, turned on check box '",
     "     VISIBLE:  '<x> cb4: readOnly checkbox, turn', cursor=0",
     "SPEECH OUTPUT: 'cb4: readOnly checkbox, turned on check box checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "7. Tab to the cb5 checkbox",
    ["BRAILLE LINE:  '< > cb5: normal checkbox, with specified value=\"\", clicking generates console log messages check box  get('value') push button'",
     "     VISIBLE:  '< > cb5: normal checkbox, with s', cursor=0",
     "SPEECH OUTPUT: 'cb5: normal checkbox, with specified value=\"\", clicking generates console log messages check box not checked'"]))

sequence.append(KeyComboAction("Tab"))
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "8. Tab to the cb6 checkbox",
    ["BRAILLE LINE:  '<x> cb6: instantiated from script check box '",
     "     VISIBLE:  '<x> cb6: instantiated from scrip', cursor=0",
     "SPEECH OUTPUT: 'cb6: instantiated from script check box checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "9. Tab to the cb7 checkbox",
    ["BRAILLE LINE:  '< > cb7: normal checkbox. check box  disable push button enable push button set value to \"fish\" push button Reset value+checked push button \"onChange\" handler updates: []'",
     "     VISIBLE:  '< > cb7: normal checkbox. check ', cursor=0",
     "SPEECH OUTPUT: 'cb7: normal checkbox. check box not checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "10. Basic Where Am I",
    ["BRAILLE LINE:  '< > cb7: normal checkbox. check box  disable push button enable push button set value to \"fish\" push button Reset value+checked push button \"onChange\" handler updates: []'",
     "     VISIBLE:  '< > cb7: normal checkbox. check ', cursor=0",
     "SPEECH OUTPUT: 'cb7: normal checkbox.'",
     "SPEECH OUTPUT: 'check box not checked'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
