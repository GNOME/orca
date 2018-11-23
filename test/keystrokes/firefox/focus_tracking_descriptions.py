#!/usr/bin/python

"""Test of the fix for bug 511389."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

#sequence.append(WaitForDocLoad())
sequence.append(PauseAction(5000))
sequence.append(KeyComboAction("<Control>Home"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "1. Tab",
    ["BRAILLE LINE:  'Foo'",
     "     VISIBLE:  'Foo', cursor=1",
     "SPEECH OUTPUT: 'Foo link.'",
     "SPEECH OUTPUT: 'Title of the Foo link.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "2. Tab",
    ["BRAILLE LINE:  'Bar'",
     "     VISIBLE:  'Bar', cursor=1",
     "SPEECH OUTPUT: 'Bar link.'",
     "SPEECH OUTPUT: 'ARIA description text.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "3. Tab",
    ["BRAILLE LINE:  'Baz'",
     "     VISIBLE:  'Baz', cursor=1",
     "SPEECH OUTPUT: 'Baz link.'",
     "SPEECH OUTPUT: 'Title of the Baz link.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "4. Tab",
    ["BRAILLE LINE:  '< > Title of the Black checkbox check box'",
     "     VISIBLE:  '< > Title of the Black checkbox ', cursor=1",
     "SPEECH OUTPUT: 'Title of the Black checkbox check box not checked.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "5. Tab",
    ["BRAILLE LINE:  '< > Title of the White checkbox check box'",
     "     VISIBLE:  '< > Title of the White checkbox ', cursor=1",
     "SPEECH OUTPUT: 'Title of the White checkbox check box not checked.'",
     "SPEECH OUTPUT: 'ARIA description text.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "6. Tab",
    ["BRAILLE LINE:  '< > Title of the Grey checkbox check box'",
     "     VISIBLE:  '< > Title of the Grey checkbox c', cursor=1",
     "SPEECH OUTPUT: 'Title of the Grey checkbox check box not checked.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "7. Tab",
    ["BRAILLE LINE:  '< > Black check box'",
     "     VISIBLE:  '< > Black check box', cursor=1",
     "SPEECH OUTPUT: 'Black check box not checked.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "8. Tab",
    ["BRAILLE LINE:  '< > White check box'",
     "     VISIBLE:  '< > White check box', cursor=1",
     "SPEECH OUTPUT: 'White check box not checked.'",
     "SPEECH OUTPUT: 'ARIA description text.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "9. Tab",
    ["BRAILLE LINE:  '< > Grey check box'",
     "     VISIBLE:  '< > Grey check box', cursor=1",
     "SPEECH OUTPUT: 'Grey check box not checked.'",
     "SPEECH OUTPUT: 'Title of the Grey checkbox'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
