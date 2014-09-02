#!/usr/bin/python

"""Test of line navigation output of Firefox."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(KeyComboAction("<Control>Home"))
sequence.append(KeyComboAction("Down"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Right"))
sequence.append(utils.AssertPresentationAction(
    "1. Next Word",
    ["BRAILLE LINE:  'Hello W o r ld. Goodbye world.'",
     "     VISIBLE:  'Hello W o r ld. Goodbye world.', cursor=6",
     "SPEECH OUTPUT: 'Hello '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Right"))
sequence.append(utils.AssertPresentationAction(
    "2. Next Word",
    ["BRAILLE LINE:  'Hello W o r ld. Goodbye world.'",
     "     VISIBLE:  'Hello W o r ld. Goodbye world.', cursor=16",
     "SPEECH OUTPUT: 'W'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: 'o'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: 'r'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: 'l'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: 'd. '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Right"))
sequence.append(utils.AssertPresentationAction(
    "3. Next Word",
    ["BRAILLE LINE:  'Hello W o r ld. Goodbye world.'",
     "     VISIBLE:  'Hello W o r ld. Goodbye world.', cursor=19",
     "SPEECH OUTPUT: 'Go'",
     "SPEECH OUTPUT: 'odbye '",
     "SPEECH OUTPUT: 'link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Right"))
sequence.append(utils.AssertPresentationAction(
    "4. Next Word",
    ["BRAILLE LINE:  ''",
     "     VISIBLE:  '', cursor=1",
     "SPEECH OUTPUT: 'w'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: 'orld.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Right"))
sequence.append(utils.AssertPresentationAction(
    "5. Next Word",
    ["BRAILLE LINE:  'More stuff! Yay!'",
     "     VISIBLE:  'More stuff! Yay!', cursor=5",
     "SPEECH OUTPUT: 'More '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Right"))
sequence.append(utils.AssertPresentationAction(
    "6. Next Word",
    ["BRAILLE LINE:  'More stuff! Yay!'",
     "     VISIBLE:  'More stuff! Yay!', cursor=12",
     "SPEECH OUTPUT: 'stuff'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: '! '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Left"))
sequence.append(utils.AssertPresentationAction(
    "7. Previous Word",
    ["BRAILLE LINE:  'More stuff! Yay!'",
     "     VISIBLE:  'More stuff! Yay!', cursor=6",
     "SPEECH OUTPUT: 'stuff'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: '! '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Left"))
sequence.append(utils.AssertPresentationAction(
    "8. Previous Word",
    ["BRAILLE LINE:  'More stuff! Yay!'",
     "     VISIBLE:  'More stuff! Yay!', cursor=1",
     "SPEECH OUTPUT: 'More '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Left"))
sequence.append(utils.AssertPresentationAction(
    "9. Previous Word",
    ["BRAILLE LINE:  'Hello W o r ld. Go orld.odbye w'",
     "     VISIBLE:  'Hello W o r ld. Go orld.odbye w', cursor=25",
     "SPEECH OUTPUT: 'w'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: 'orld.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Left"))
sequence.append(utils.AssertPresentationAction(
    "10. Previous Word",
    ["BRAILLE LINE:  'Hello W o r ld. Goodbye world.'",
     "     VISIBLE:  'Hello W o r ld. Goodbye world.', cursor=17",
     "SPEECH OUTPUT: 'Go'",
     "SPEECH OUTPUT: 'odbye '",
     "SPEECH OUTPUT: 'link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Left"))
sequence.append(utils.AssertPresentationAction(
    "11. Previous Word",
    ["BRAILLE LINE:  'Hello W o r ld. Goodbye world.'",
     "     VISIBLE:  'Hello W o r ld. Goodbye world.', cursor=7",
     "SPEECH OUTPUT: 'W'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: 'o'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: 'r'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: 'l'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: 'd. '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Left"))
sequence.append(utils.AssertPresentationAction(
    "12. Previous Word",
    ["BRAILLE LINE:  'Hello W o r ld. Goodbye world.'",
     "     VISIBLE:  'Hello W o r ld. Goodbye world.', cursor=1",
     "SPEECH OUTPUT: 'Hello '"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
