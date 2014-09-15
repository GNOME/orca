#!/usr/bin/python

"""Test of structural navigation."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(KeyComboAction("<Control>Home"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("k"))
sequence.append(utils.AssertPresentationAction(
    "1. k for next link",
    ["BRAILLE LINE:  'Foo, Bar, and Baz.'",
     "     VISIBLE:  'Foo, Bar, and Baz.', cursor=1",
     "SPEECH OUTPUT: 'Foo'",
     "SPEECH OUTPUT: 'link Title of the Foo link.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("k"))
sequence.append(utils.AssertPresentationAction(
    "2. k for next link",
    ["BRAILLE LINE:  'Foo, Bar, and Baz.'",
     "     VISIBLE:  'Foo, Bar, and Baz.', cursor=6",
     "SPEECH OUTPUT: 'Bar'",
     "SPEECH OUTPUT: 'link ARIA description text.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("k"))
sequence.append(utils.AssertPresentationAction(
    "3. k for next link",
    ["BRAILLE LINE:  'Foo, Bar, and Baz.'",
     "     VISIBLE:  'Foo, Bar, and Baz.', cursor=15",
     "SPEECH OUTPUT: 'Baz'",
     "SPEECH OUTPUT: 'link Title of the Baz link.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("x"))
sequence.append(utils.AssertPresentationAction(
    "4. x for next checkbox",
    ["BRAILLE LINE:  '< > Title of the Black checkbox check box Black < > Title of the White checkbox check box White < > Title of the Grey checkbox check box Grey'",
     "     VISIBLE:  '< > Title of the Black checkbox ', cursor=1",
     "SPEECH OUTPUT: 'Title of the Black checkbox check box not checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("x"))
sequence.append(utils.AssertPresentationAction(
    "5. x for next checkbox",
    ["BRAILLE LINE:  '< > Title of the Black checkbox check box Black < > Title of the White checkbox check box White < > Title of the Grey checkbox check box Grey'",
     "     VISIBLE:  '< > Title of the White checkbox ', cursor=1",
     "SPEECH OUTPUT: 'Title of the White checkbox check box not checked ARIA description text.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("x"))
sequence.append(utils.AssertPresentationAction(
    "6. x for next checkbox",
    ["BRAILLE LINE:  '< > Title of the Black checkbox check box Black < > Title of the White checkbox check box White < > Title of the Grey checkbox check box Grey'",
     "     VISIBLE:  '< > Title of the Grey checkbox c', cursor=1",
     "SPEECH OUTPUT: 'Title of the Grey checkbox check box not checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("x"))
sequence.append(utils.AssertPresentationAction(
    "7. x for next checkbox",
    ["BRAILLE LINE:  '< > Black check box < > White check box < > Grey check box'",
     "     VISIBLE:  '< > Black check box < > White ch', cursor=1",
     "SPEECH OUTPUT: 'Black check box not checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("x"))
sequence.append(utils.AssertPresentationAction(
    "8. x for next checkbox",
    ["BRAILLE LINE:  '< > Black check box < > White check box < > Grey check box'",
     "     VISIBLE:  '< > White check box < > Grey che', cursor=1",
     "SPEECH OUTPUT: 'White check box not checked ARIA description text.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("x"))
sequence.append(utils.AssertPresentationAction(
    "9. x for next checkbox",
    ["BRAILLE LINE:  '< > Black check box < > White check box < > Grey check box'",
     "     VISIBLE:  '< > Grey check box', cursor=1",
     "SPEECH OUTPUT: 'Grey check box not checked Title of the Grey checkbox'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
