#!/usr/bin/python

"""Test of menu and menu item output."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(KeyComboAction("<Control>f"))
sequence.append(TypeAction("Application main window"))
sequence.append(KeyComboAction("Return"))
sequence.append(KeyComboAction("Return"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt>p"))
sequence.append(utils.AssertPresentationAction(
    "1. Initial menu and menu item",
    ["BRAILLE LINE:  'gtk-demo application Application Window frame Preferences menu'",
     "     VISIBLE:  'Preferences menu', cursor=1",
     "BRAILLE LINE:  'gtk-demo application Application Window frame Color menu'",
     "     VISIBLE:  'Color menu', cursor=1",
     "SPEECH OUTPUT: 'Preferences menu.'",
     "SPEECH OUTPUT: 'Color menu.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_8"))
sequence.append(utils.AssertPresentationAction(
    "2. Review current line",
    ["KNOWN ISSUE: Menu items are not currently reviewable. Thus all the following assertions are wrong.",
     "BRAILLE LINE:  'File Preferences Help $l'",
     "     VISIBLE:  'File Preferences Help $l', cursor=1",
     "SPEECH OUTPUT: 'File Preferences Help'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_7"))
sequence.append(utils.AssertPresentationAction(
    "3. Review previous line",
    [""]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_9"))
sequence.append(utils.AssertPresentationAction(
    "4. Review next line",
    ["BRAILLE LINE:  'Open & y toggle button Quit GTK! $l'",
     "     VISIBLE:  'Open & y toggle button Quit GTK!', cursor=1",
     "SPEECH OUTPUT: 'Open not pressed toggle button Quit GTK!'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_5"))
sequence.append(utils.AssertPresentationAction(
    "5. Review current word",
    ["BRAILLE LINE:  'Open & y toggle button Quit GTK! $l'",
     "     VISIBLE:  'Open & y toggle button Quit GTK!', cursor=1",
     "SPEECH OUTPUT: 'Open'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_6"))
sequence.append(utils.AssertPresentationAction(
    "6. Review next word",
    ["BRAILLE LINE:  'Open & y toggle button Quit GTK! $l'",
     "     VISIBLE:  'Open & y toggle button Quit GTK!', cursor=6",
     "SPEECH OUTPUT: 'not pressed'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_9"))
sequence.append(utils.AssertPresentationAction(
    "7. Review next line",
    ["BRAILLE LINE:  'text $l'",
     "     VISIBLE:  'text $l', cursor=1",
     "SPEECH OUTPUT: 'text'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_5"))
sequence.append(utils.AssertPresentationAction(
    "8. Review current word",
    ["BRAILLE LINE:  'text $l'",
     "     VISIBLE:  'text $l', cursor=1",
     "SPEECH OUTPUT: 'text'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_2"))
sequence.append(utils.AssertPresentationAction(
    "9. Review current char",
    ["BRAILLE LINE:  'text $l'",
     "     VISIBLE:  'text $l', cursor=1",
     "SPEECH OUTPUT: 'text'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_6"))
sequence.append(utils.AssertPresentationAction(
    "10. Review next word",
    ["BRAILLE LINE:  'Cursor at row 0 column 0 - 0 chars in document $l'",
     "     VISIBLE:  'Cursor at row 0 column 0 - 0 cha', cursor=1",
     "SPEECH OUTPUT: 'Cursor '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_3"))
sequence.append(utils.AssertPresentationAction(
    "11. Review next char",
    ["BRAILLE LINE:  'Cursor at row 0 column 0 - 0 chars in document $l'",
     "     VISIBLE:  'Cursor at row 0 column 0 - 0 cha', cursor=2",
     "SPEECH OUTPUT: 'u'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_1"))
sequence.append(utils.AssertPresentationAction(
    "12. Review previous char",
    ["BRAILLE LINE:  'Cursor at row 0 column 0 - 0 chars in document $l'",
     "     VISIBLE:  'Cursor at row 0 column 0 - 0 cha', cursor=1",
     "SPEECH OUTPUT: 'C'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_1"))
sequence.append(utils.AssertPresentationAction(
    "13. Review previous char",
    ["BRAILLE LINE:  'text $l'",
     "     VISIBLE:  'text $l', cursor=1",
     "SPEECH OUTPUT: 'text'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_4"))
sequence.append(utils.AssertPresentationAction(
    "14. Review previous word",
    ["BRAILLE LINE:  'Open & y toggle button Quit GTK! $l'",
     "     VISIBLE:  'Open & y toggle button Quit GTK!', cursor=29",
     "SPEECH OUTPUT: 'GTK!'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_7"))
sequence.append(utils.AssertPresentationAction(
    "15. Review previous line",
    ["BRAILLE LINE:  'File Preferences Help $l'",
     "     VISIBLE:  'File Preferences Help $l', cursor=1",
     "SPEECH OUTPUT: 'File Preferences Help'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
