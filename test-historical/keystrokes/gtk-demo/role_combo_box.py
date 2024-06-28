#!/usr/bin/python

"""Test of combobox output."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(KeyComboAction("<Control>f"))
sequence.append(TypeAction("Combo boxes"))
sequence.append(KeyComboAction("Return"))

sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction(" "))
sequence.append(utils.AssertPresentationAction(
    "1. Warning combo box item",
    ["BRAILLE LINE:  'gtk-demo application Combo boxes frame Some stock icons panel menu'",
     "     VISIBLE:  'menu', cursor=1",
     "BRAILLE LINE:  'gtk-demo application Combo boxes frame Some stock icons panel Warning combo box Warning'",
     "     VISIBLE:  'Warning', cursor=1",
     "SPEECH OUTPUT: 'combo box.'",
     "SPEECH OUTPUT: 'Warning.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "2. Warning combo box item Where Am I",
    ["BRAILLE LINE:  'gtk-demo application Combo boxes frame Some stock icons panel Warning combo box Warning'",
     "     VISIBLE:  'Warning', cursor=1",
     "SPEECH OUTPUT: 'Combo boxes frame'",
     "SPEECH OUTPUT: 'Some stock icons panel.'",
     "SPEECH OUTPUT: 'Warning.'",
     "SPEECH OUTPUT: '1 of 5'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "3. New combo box item",
    ["BRAILLE LINE:  'gtk-demo application Combo boxes frame Some stock icons panel Warning combo box New'",
     "     VISIBLE:  'New', cursor=1",
     "SPEECH OUTPUT: 'New.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "4. New combo box item Where Am I",
    ["BRAILLE LINE:  'gtk-demo application Combo boxes frame Some stock icons panel Warning combo box New'",
     "     VISIBLE:  'New', cursor=1",
     "SPEECH OUTPUT: 'Combo boxes frame'",
     "SPEECH OUTPUT: 'Some stock icons panel.'",
     "SPEECH OUTPUT: 'New.'",
     "SPEECH OUTPUT: '3 of 5'"]))

sequence.append(KeyComboAction("Escape"))
sequence.append(KeyComboAction("Tab"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "5. Editable text combo box",
    ["BRAILLE LINE:  'gtk-demo application Combo boxes frame Editable panel  $l'",
     "     VISIBLE:  'boxes frame Editable panel  $l', cursor=28",
     "SPEECH OUTPUT: 'Editable panel.'",
     "SPEECH OUTPUT: 'editable combo box.'"]))

sequence.append(TypeAction("Fou"))
sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction("r"))
sequence.append(utils.AssertPresentationAction(
    "6. Editable text combo box typing",
    ["BRAILLE LINE:  'gtk-demo application Combo boxes frame Editable panel Fou $l'",
     "     VISIBLE:  'boxes frame Editable panel Fou $', cursor=32",
     "BRAILLE LINE:  'gtk-demo application Combo boxes frame Editable panel Four $l'",
     "     VISIBLE:  'boxes frame Editable panel Four ', cursor=32"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "7. Editable text combo box Where Am I",
    ["BRAILLE LINE:  'gtk-demo application Combo boxes frame Editable panel Four $l'",
     "     VISIBLE:  'boxes frame Editable panel Four ', cursor=32",
     "SPEECH OUTPUT: 'editable combo box.'",
     "SPEECH OUTPUT: 'Four.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "8. Editable text combo box open button",
    ["BRAILLE LINE:  'gtk-demo application Combo boxes frame Editable panel Four $l combo box'",
     "     VISIBLE:  'boxes frame Editable panel Four ', cursor=32",
     "SPEECH OUTPUT: 'Four editable combo box.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>ISO_Left_Tab"))
sequence.append(utils.AssertPresentationAction(
    "9. Editable text combo box with selected text",
    ["BRAILLE LINE:  'gtk-demo application Combo boxes frame Editable panel Four $l'",
     "     VISIBLE:  'boxes frame Editable panel Four ', cursor=32",
     "BRAILLE LINE:  'gtk-demo application Combo boxes frame Editable panel Four $l'",
     "     VISIBLE:  'boxes frame Editable panel Four ', cursor=32",
     "SPEECH OUTPUT: 'editable combo box.'",
     "SPEECH OUTPUT: 'Four selected'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "10. Editable text combo box with selected text Where Am I",
    ["BRAILLE LINE:  'gtk-demo application Combo boxes frame Editable panel Four $l'",
     "     VISIBLE:  'boxes frame Editable panel Four ', cursor=32",
     "SPEECH OUTPUT: 'editable combo box.'",
     "SPEECH OUTPUT: 'Four selected.'"]))

sequence.append(KeyComboAction("Escape"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("Tab"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "11. Combo box with multiple levels",
    ["BRAILLE LINE:  'gtk-demo application Combo boxes frame Where are we ? panel Boston combo box'",
     "     VISIBLE:  'Boston combo box', cursor=1",
     "SPEECH OUTPUT: 'Where are we ? panel.'",
     "SPEECH OUTPUT: 'Boston combo box.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "12. Down arrow",
    ["KNOWN ISSUE: Gtk+ has missing events and a broken selection interface in multi-level combo boxes",
     ""]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "13. Where Am I",
    ["KNOWN ISSUE: The count is wrong due to a Gtk+ 2 bug which has been fixed in Gtk+ 3",
     "BRAILLE LINE:  'gtk-demo application Combo boxes frame Where are we ? panel Carson City combo box'",
     "     VISIBLE:  'Carson City combo box', cursor=1",
     "SPEECH OUTPUT: 'combo box.'",
     "SPEECH OUTPUT: 'Carson City 1 of 1'"]))

sequence.append(KeyComboAction("<Alt>F4"))
sequence.append(utils.AssertionSummaryAction())
sequence.start()
