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
    "Warning combo box item",
    ["BRAILLE LINE:  'gtk-demo application Combo boxes frame'",
     "     VISIBLE:  'Combo boxes frame', cursor=1",
     "BRAILLE LINE:  'gtk-demo application Combo boxes frame Items with icons panel Warning combo box'",
     "     VISIBLE:  'Warning combo box', cursor=1",
     "SPEECH OUTPUT: 'Combo boxes frame'",
     "SPEECH OUTPUT: 'Items with icons panel'",
     "SPEECH OUTPUT: 'Warning combo box'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "Warning combo box item Where Am I",
    ["BRAILLE LINE:  'gtk-demo application Combo boxes frame Items with icons panel Warning combo box'",
     "     VISIBLE:  'Warning combo box', cursor=1",
     "SPEECH OUTPUT: 'combo box'",
     "SPEECH OUTPUT: 'Warning'",
     "SPEECH OUTPUT: '1 of 5'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "New combo box item",
    ["BRAILLE LINE:  'gtk-demo application Combo boxes frame Items with icons panel  combo boxNew New'",
     "     VISIBLE:  'New', cursor=1",
     "SPEECH OUTPUT: 'New'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "New combo box item Where Am I",
    ["KNOWN ISSUE: We're a bit chatty here and have some spacing issues",
     "BRAILLE LINE:  'gtk-demo application Combo boxes frame Items with icons panel  combo boxNew New'",
     "     VISIBLE:  'New', cursor=1",
     "SPEECH OUTPUT: 'Combo boxes'",
     "SPEECH OUTPUT: 'frame'",
     "SPEECH OUTPUT: 'Items with icons'",
     "SPEECH OUTPUT: 'panel'",
     "SPEECH OUTPUT: 'New'",
     "SPEECH OUTPUT: 'combo box'",
     "SPEECH OUTPUT: 'New'",
     "SPEECH OUTPUT: '3 of 5'"]))

sequence.append(KeyComboAction("Tab"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "Editable text combo box",
    ["BRAILLE LINE:  'gtk-demo application Combo boxes frame Editable panel  $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "SPEECH OUTPUT: 'Editable panel'",
     "SPEECH OUTPUT: 'text'"]))

sequence.append(TypeAction("Fou"))
sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction("r"))
sequence.append(utils.AssertPresentationAction(
    "Editable text combo box typing",
    ["BRAILLE LINE:  'gtk-demo application Combo boxes frame Editable panel Four $l'",
     "     VISIBLE:  'Four $l', cursor=5",
     "BRAILLE LINE:  'gtk-demo application Combo boxes frame Editable panel Four $l'",
     "     VISIBLE:  'Four $l', cursor=5"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "Editable text combo box Where Am I",
    ["BRAILLE LINE:  'gtk-demo application Combo boxes frame Editable panel Four $l'",
     "     VISIBLE:  'Four $l', cursor=5",
     "SPEECH OUTPUT: 'text'",
     "SPEECH OUTPUT: 'Four'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "Editable text combo box open button",
    ["BRAILLE LINE:  'gtk-demo application Combo boxes frame Editable panel Four $l combo box'",
     "     VISIBLE:  'Four $l combo box', cursor=5",
     "SPEECH OUTPUT: 'Four combo box'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>ISO_Left_Tab"))
sequence.append(utils.AssertPresentationAction(
    "Editable text combo box with selected text",
    ["BRAILLE LINE:  'gtk-demo application Combo boxes frame Editable panel Four $l'",
     "     VISIBLE:  'Four $l', cursor=5",
     "BRAILLE LINE:  'gtk-demo application Combo boxes frame Editable panel Four $l'",
     "     VISIBLE:  'Four $l', cursor=5",
     "SPEECH OUTPUT: 'text Four selected'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "Editable text combo box with selected text Where Am I",
    ["BRAILLE LINE:  'gtk-demo application Combo boxes frame Editable panel Four $l'",
     "     VISIBLE:  'Four $l', cursor=5",
     "SPEECH OUTPUT: 'text'",
     "SPEECH OUTPUT: 'Four'",
     "SPEECH OUTPUT: 'selected'"]))

sequence.append(KeyComboAction("<Alt>F4"))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
