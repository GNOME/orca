#!/usr/bin/python

"""Test of line navigation output of Firefox."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(KeyComboAction("<Control>Home"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "1. Line Down",
    ["BRAILLE LINE:  'Foo, Bar, and Baz.'",
     "     VISIBLE:  'Foo, Bar, and Baz.', cursor=1",
     "SPEECH OUTPUT: 'Foo'",
     "SPEECH OUTPUT: 'link Title of the Foo link.'",
     "SPEECH OUTPUT: ','",
     "SPEECH OUTPUT: 'Bar'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: ', and'",
     "SPEECH OUTPUT: 'Baz'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: '.'"]))

sequence.append(KeyComboAction("Down"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "2. Line Down",
    ["BRAILLE LINE:  '< > Title of the Black checkbox check box Black < > Title of the White checkbox check box White < > Title of the Grey checkbox check box Grey'",
     "     VISIBLE:  '< > Title of the Black checkbox ', cursor=0",
     "SPEECH OUTPUT: 'Title of the Black checkbox check box not checked'",
     "SPEECH OUTPUT: 'Black'",
     "SPEECH OUTPUT: 'Title of the White checkbox check box not checked'",
     "SPEECH OUTPUT: 'White'",
     "SPEECH OUTPUT: 'Title of the Grey checkbox check box not checked'",
     "SPEECH OUTPUT: 'Grey'"]))

sequence.append(KeyComboAction("Down"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "3. Line Down",
    ["BRAILLE LINE:  '< > Black check box < > White check box < > Grey check box'",
     "     VISIBLE:  '< > Black check box < > White ch', cursor=0",
     "SPEECH OUTPUT: 'Black check box not checked'",
     "SPEECH OUTPUT: 'White check box not checked'",
     "SPEECH OUTPUT: 'Grey check box not checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "3. Line Down to aria-hidden line",
    [""]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
