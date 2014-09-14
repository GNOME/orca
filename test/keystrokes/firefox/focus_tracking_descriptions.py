#!/usr/bin/python

"""Test of the fix for bug 511389."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(KeyComboAction("<Control>Home"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "1. Tab",
    ["BRAILLE LINE:  'Foo, Bar, and Baz.'",
     "     VISIBLE:  'Foo, Bar, and Baz.', cursor=1",
     "BRAILLE LINE:  'Foo, Bar, and Baz.'",
     "     VISIBLE:  'Foo, Bar, and Baz.', cursor=1",
     "SPEECH OUTPUT: 'Foo link Title of the Foo link.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "2. Tab",
    ["BRAILLE LINE:  'Foo, Bar, and Baz.'",
     "     VISIBLE:  'Foo, Bar, and Baz.', cursor=6",
     "BRAILLE LINE:  'Foo, Bar, and Baz.'",
     "     VISIBLE:  'Foo, Bar, and Baz.', cursor=6",
     "SPEECH OUTPUT: 'Bar link ARIA description text.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "3. Tab",
    ["BRAILLE LINE:  'Foo, Bar, and Baz.'",
     "     VISIBLE:  'Foo, Bar, and Baz.', cursor=15",
     "BRAILLE LINE:  'Foo, Bar, and Baz.'",
     "     VISIBLE:  'Foo, Bar, and Baz.', cursor=15",
     "SPEECH OUTPUT: 'Baz link Title of the Baz link.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "4. Tab",
    ["BRAILLE LINE:  '< > Title of the Black checkbox check box Black < > Title of the White checkbox check box White < > Title of the Grey checkbox check box Grey'",
     "     VISIBLE:  '< > Title of the Black checkbox ', cursor=0",
     "SPEECH OUTPUT: 'Title of the Black checkbox check box not checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "5. Tab",
    ["KNOWN ISSUE: We're not scrolling braille",
     "BRAILLE LINE:  '< > Title of the Black checkbox check box Black < > Title of the White checkbox check box White < > Title of the Grey checkbox check box Grey'",
     "     VISIBLE:  '< > Title of the Black checkbox ', cursor=0",
     "SPEECH OUTPUT: 'Title of the White checkbox check box not checked ARIA description text.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "6. Tab",
    ["KNOWN ISSUE: We're not scrolling braille",
     "BRAILLE LINE:  '< > Title of the Black checkbox check box Black < > Title of the White checkbox check box White < > Title of the Grey checkbox check box Grey'",
     "     VISIBLE:  '< > Title of the Black checkbox ', cursor=0",
     "SPEECH OUTPUT: 'Title of the Grey checkbox check box not checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "7. Tab",
    ["KNOWN ISSUE: We're not scrolling braille",
     "BRAILLE LINE:  '< > Black check box < > White check box < > Grey check box'",
     "     VISIBLE:  '< > Black check box < > White ch', cursor=0",
     "SPEECH OUTPUT: 'Black check box not checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "8. Tab",
    ["KNOWN ISSUE: We're not scrolling braille",
     "BRAILLE LINE:  '< > Black check box < > White check box < > Grey check box'",
     "     VISIBLE:  '< > Black check box < > White ch', cursor=0",
     "SPEECH OUTPUT: 'White check box not checked ARIA description text.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "9. Tab",
    ["KNOWN ISSUE: We're not scrolling braille",
     "BRAILLE LINE:  '< > Black check box < > White check box < > Grey check box'",
     "     VISIBLE:  '< > Black check box < > White ch', cursor=0",
     "SPEECH OUTPUT: 'Grey check box not checked Title of the Grey checkbox'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
