#!/usr/bin/python

"""Test of combobox output."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(KeyComboAction("<Control>f"))
sequence.append(TypeAction("Combo boxes"))
sequence.append(KeyComboAction("Return"))
sequence.append(PauseAction(3000))

sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction(" "))
sequence.append(utils.AssertPresentationAction(
    "1. Warning combo box item",
    ["BRAILLE LINE:  'gtk3-demo application Combo boxes frame'",
     "     VISIBLE:  'Combo boxes frame', cursor=1",
     "BRAILLE LINE:  'gtk3-demo application Combo boxes frame Items with icons panel Warning combo box'",
     "     VISIBLE:  'Warning combo box', cursor=1",
     "SPEECH OUTPUT: 'Combo boxes frame'",
     "SPEECH OUTPUT: 'Items with icons panel'",
     "SPEECH OUTPUT: 'Warning combo box'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "2. Warning combo box item Where Am I",
    ["BRAILLE LINE:  'gtk3-demo application Combo boxes frame Items with icons panel Warning combo box'",
     "     VISIBLE:  'Warning combo box', cursor=1",
     "SPEECH OUTPUT: 'combo box Warning 1 of 5'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "3. New combo box item",
    ["BRAILLE LINE:  'gtk3-demo application Combo boxes frame Items with icons panel  combo boxNew New'",
     "     VISIBLE:  'New', cursor=1",
     "SPEECH OUTPUT: 'New'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "4. New combo box item Where Am I",
    ["KNOWN ISSUE: The combo box role is missing and spacing is wrong in braille",
     "BRAILLE LINE:  'gtk3-demo application Combo boxes frame Items with icons panel  combo boxNew New'",
     "     VISIBLE:  'New', cursor=1",
     "SPEECH OUTPUT: 'Combo boxes frame'",
     "SPEECH OUTPUT: 'Items with icons panel'",
     "SPEECH OUTPUT: 'New 3 of 5'"]))

sequence.append(KeyComboAction("Tab"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "5. Editable text combo box",
    ["BRAILLE LINE:  'gtk3-demo application Combo boxes frame Editable panel  $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "SPEECH OUTPUT: 'Editable panel'",
     "SPEECH OUTPUT: 'text'"]))

sequence.append(TypeAction("Fou"))
sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction("r"))
sequence.append(utils.AssertPresentationAction(
    "6. Editable text combo box typing",
    ["BRAILLE LINE:  'gtk3-demo application Combo boxes frame Editable panel Four $l'",
     "     VISIBLE:  'Four $l', cursor=5",
     "BRAILLE LINE:  'gtk3-demo application Combo boxes frame Editable panel Four $l'",
     "     VISIBLE:  'Four $l', cursor=5"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "7. Editable text combo box Where Am I",
    ["BRAILLE LINE:  'gtk3-demo application Combo boxes frame Editable panel Four $l'",
     "     VISIBLE:  'Four $l', cursor=5",
     "SPEECH OUTPUT: 'text Four'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "8. Editable text combo box open button",
    ["BRAILLE LINE:  'gtk3-demo application Combo boxes frame Editable panel Four $l combo box'",
     "     VISIBLE:  'Four $l combo box', cursor=5",
     "SPEECH OUTPUT: 'Four combo box'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>ISO_Left_Tab"))
sequence.append(utils.AssertPresentationAction(
    "9. Editable text combo box with selected text",
    ["BRAILLE LINE:  'gtk3-demo application Combo boxes frame Editable panel Four $l'",
     "     VISIBLE:  'Four $l', cursor=5",
     "BRAILLE LINE:  'gtk3-demo application Combo boxes frame Editable panel Four $l'",
     "     VISIBLE:  'Four $l', cursor=5",
     "SPEECH OUTPUT: 'text Four selected'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "10. Editable text combo box with selected text Where Am I",
    ["BRAILLE LINE:  'gtk3-demo application Combo boxes frame Editable panel Four $l'",
     "     VISIBLE:  'Four $l', cursor=5",
     "SPEECH OUTPUT: 'text Four selected'"]))

sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("Tab"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "11. Combo box with multiple levels",
    ["KNOWN ISSUE: This is broken",
     "BRAILLE LINE:  'gtk3-demo application Combo boxes frame Where are we ? panel A - B combo box'",
     "     VISIBLE:  'A - B combo box', cursor=1",
     "SPEECH OUTPUT: 'Where are we ? panel'",
     "SPEECH OUTPUT: 'A - B combo box'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "12. Down arrow",
    ["KNOWN ISSUE: This is broken",
     "BRAILLE LINE:  'gtk3-demo application Combo boxes frame Where are we ? panel  combo boxC - D C - D menu'",
     "     VISIBLE:  'C - D menu', cursor=1",
     "SPEECH OUTPUT: 'C - D menu'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "12. Where Am I",
    ["KNOWN ISSUE: This is broken",
     "BRAILLE LINE:  'gtk3-demo application Combo boxes frame Where are we ? panel  combo boxC - D C - D menu'",
     "     VISIBLE:  'C - D menu', cursor=1",
     "SPEECH OUTPUT: 'Combo boxes frame'",
     "SPEECH OUTPUT: 'Where are we ? panel'",
     "SPEECH OUTPUT: 'C - D menu 2 of 5'"]))

sequence.append(KeyComboAction("<Alt>F4"))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
