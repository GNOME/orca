#!/usr/bin/python

"""Test for structural navigation amongst table cells in Writer."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(KeyComboAction("<Control>Home"))
sequence.append(KeyComboAction("Down"))
sequence.append(KeyComboAction("Down"))
sequence.append(KeyComboAction("Down"))
sequence.append(KeyComboAction("Down"))
sequence.append(PauseAction(3000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("z"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "1. Toggle structural navigation on",
    ["BRAILLE LINE:  'Structural navigation keys on.'",
     "     VISIBLE:  'Structural navigation keys on.', cursor=0",
     "SPEECH OUTPUT: 'Structural navigation keys on.' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt><Shift>Left"))
sequence.append(utils.AssertPresentationAction(
    "2. Alt Shift Left.",
    ["BRAILLE LINE:  '4 $l'",
     "     VISIBLE:  '4 $l', cursor=2",
     "BRAILLE LINE:  '3 $l'",
     "     VISIBLE:  '3 $l', cursor=1",
     "BRAILLE LINE:  'Row 3, column 1.'",
     "     VISIBLE:  'Row 3, column 1.', cursor=0",
     "SPEECH OUTPUT: '3.'",
     "SPEECH OUTPUT: 'Row 3, column 1.' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt><Shift>Left"))
sequence.append(utils.AssertPresentationAction(
    "3. Alt Shift Left.",
    ["BRAILLE LINE:  '3 $l'",
     "     VISIBLE:  '3 $l', cursor=1",
     "BRAILLE LINE:  'Beginning of row.'",
     "     VISIBLE:  'Beginning of row.', cursor=0",
     "SPEECH OUTPUT: 'Beginning of row.' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt><Shift>Right"))
sequence.append(utils.AssertPresentationAction(
    "4. Alt Shift Right.",
    ["BRAILLE LINE:  '3 $l'",
     "     VISIBLE:  '3 $l', cursor=1",
     "BRAILLE LINE:  '4 $l'",
     "     VISIBLE:  '4 $l', cursor=1",
     "BRAILLE LINE:  'Row 3, column 2.'",
     "     VISIBLE:  'Row 3, column 2.', cursor=0",
     "SPEECH OUTPUT: '4.'",
     "SPEECH OUTPUT: 'Row 3, column 2.' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt><Shift>Right"))
sequence.append(utils.AssertPresentationAction(
    "5. Alt Shift Right.",
    ["BRAILLE LINE:  '4 $l'",
     "     VISIBLE:  '4 $l', cursor=1",
     "BRAILLE LINE:  '5 $l'",
     "     VISIBLE:  '5 $l', cursor=1",
     "BRAILLE LINE:  'Row 3, column 3.'",
     "     VISIBLE:  'Row 3, column 3.', cursor=0",
     "SPEECH OUTPUT: '5.'",
     "SPEECH OUTPUT: 'Row 3, column 3.' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt><Shift>Right"))
sequence.append(utils.AssertPresentationAction(
    "6. Alt Shift Right.",
    ["BRAILLE LINE:  '5 $l'",
     "     VISIBLE:  '5 $l', cursor=1",
     "BRAILLE LINE:  '6 $l'",
     "     VISIBLE:  '6 $l', cursor=1",
     "BRAILLE LINE:  'Row 3, column 4.'",
     "     VISIBLE:  'Row 3, column 4.', cursor=0",
     "BRAILLE LINE:  'Cell spans 2 columns'",
     "     VISIBLE:  'Cell spans 2 columns', cursor=0",
     "SPEECH OUTPUT: '6 7.'",
     "SPEECH OUTPUT: 'Row 3, column 4.' voice=system",
     "SPEECH OUTPUT: 'Cell spans 2 columns' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt><Shift>Up"))
sequence.append(utils.AssertPresentationAction(
    "7. Alt Shift Up.",
    ["KNOWN ISSUE: We're not presenting the 'blank'",
     "BRAILLE LINE:  '6 $l'",
     "     VISIBLE:  '6 $l', cursor=1",
     "BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "BRAILLE LINE:  'Row 2, column 4.'",
     "     VISIBLE:  'Row 2, column 4.', cursor=0",
     "SPEECH OUTPUT: 'blank.'",
     "SPEECH OUTPUT: 'Row 2, column 4.' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt><Shift>Up"))
sequence.append(utils.AssertPresentationAction(
    "8. Alt Shift Up.",
    ["BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "BRAILLE LINE:  'Wed $l'",
     "     VISIBLE:  'Wed $l', cursor=1",
     "BRAILLE LINE:  'Row 1, column 4.'",
     "     VISIBLE:  'Row 1, column 4.', cursor=0",
     "SPEECH OUTPUT: 'Wed.'",
     "SPEECH OUTPUT: 'Row 1, column 4.' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt><Shift>Up"))
sequence.append(utils.AssertPresentationAction(
    "9. Alt Shift Up.",
    ["BRAILLE LINE:  'Wed $l'",
     "     VISIBLE:  'Wed $l', cursor=1",
     "BRAILLE LINE:  'Top of column.'",
     "     VISIBLE:  'Top of column.', cursor=0",
     "SPEECH OUTPUT: 'Top of column.' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt><Shift>End"))
sequence.append(utils.AssertPresentationAction(
    "10. Alt Shift End.",
    ["KNOWN ISSUE: We're not presenting the 'blank'",
     "BRAILLE LINE:  'Wed $l'",
     "     VISIBLE:  'Wed $l', cursor=1",
     "BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "BRAILLE LINE:  'Row 7, column 7.'",
     "     VISIBLE:  'Row 7, column 7.', cursor=0",
     "SPEECH OUTPUT: 'blank.'",
     "SPEECH OUTPUT: 'Row 7, column 7.' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt><Shift>Down"))
sequence.append(utils.AssertPresentationAction(
    "11. Alt Shift Down.",
    ["BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "BRAILLE LINE:  'Bottom of column.'",
     "     VISIBLE:  'Bottom of column.', cursor=0",
     "SPEECH OUTPUT: 'Bottom of column.' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt><Shift>Right"))
sequence.append(utils.AssertPresentationAction(
    "12. Alt Shift Right.",
    ["BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "BRAILLE LINE:  'End of row.'",
     "     VISIBLE:  'End of row.', cursor=0",
     "SPEECH OUTPUT: 'End of row.' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt><Shift>Home"))
sequence.append(utils.AssertPresentationAction(
    "13. Alt Shift Home.",
    ["BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "BRAILLE LINE:  'Sun $l'",
     "     VISIBLE:  'Sun $l', cursor=1",
     "BRAILLE LINE:  'Row 1, column 1.'",
     "     VISIBLE:  'Row 1, column 1.', cursor=0",
     "SPEECH OUTPUT: 'Sun.'",
     "SPEECH OUTPUT: 'Row 1, column 1.' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt><Shift>Up"))
sequence.append(utils.AssertPresentationAction(
    "14. Alt Shift Up.",
    ["BRAILLE LINE:  'Sun $l'",
     "     VISIBLE:  'Sun $l', cursor=1",
     "BRAILLE LINE:  'Top of column.'",
     "     VISIBLE:  'Top of column.', cursor=0",
     "SPEECH OUTPUT: 'Top of column.' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "15. Up Arrow out of table.",
    ["BRAILLE LINE:  'Sun $l'",
     "     VISIBLE:  'Sun $l', cursor=1",
     "BRAILLE LINE:  'soffice application table-sample2.odt - LibreOffice Writer root pane table-sample2 - LibreOffice Document This is a test. $l'",
     "     VISIBLE:  'This is a test. $l', cursor=16",
     "SPEECH OUTPUT: 'leaving table.'",
     "SPEECH OUTPUT: 'This is a test.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt><Shift>Up"))
sequence.append(utils.AssertPresentationAction(
    "16. Alt Shift Up when not in a table.",
    ["BRAILLE LINE:  'Not in a table.'",
     "     VISIBLE:  'Not in a table.', cursor=0",
     "SPEECH OUTPUT: 'Not in a table.' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("z"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "17. Toggle structural navigation off",
    ["BRAILLE LINE:  'soffice application table-sample2.odt - LibreOffice Writer root pane table-sample2 - LibreOffice Document This is a test. $l'",
     "     VISIBLE:  'This is a test. $l', cursor=16",
     "BRAILLE LINE:  'Structural navigation keys off.'",
     "     VISIBLE:  'Structural navigation keys off.', cursor=0",
     "SPEECH OUTPUT: 'Structural navigation keys off.' voice=system"]))

sequence.append(KeyComboAction("<Alt>F4"))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
