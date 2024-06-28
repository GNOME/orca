#!/usr/bin/python

"""Test of color chooser output."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(KeyComboAction("<Control>f"))
sequence.append(TypeAction("Color Chooser"))
sequence.append(KeyComboAction("Return"))
sequence.append(KeyComboAction("Return"))
sequence.append(KeyComboAction("space"))
sequence.append(PauseAction(3000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "1. Arrow to the next swatch",
    ["BRAILLE LINE:  'gtk3-demo application Changing color dialog & y Light Orange radio button'",
     "     VISIBLE:  '& y Light Orange radio button', cursor=1",
     "SPEECH OUTPUT: 'Light Orange.'",
     "SPEECH OUTPUT: 'not selected radio button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("space"))
sequence.append(utils.AssertPresentationAction(
    "2. Space to select the current swatch",
    ["BRAILLE LINE:  'gtk3-demo application Changing color dialog &=y Light Orange radio button'",
     "     VISIBLE:  '&=y Light Orange radio button', cursor=1",
     "SPEECH OUTPUT: 'selected'"]))

sequence.append(KeyComboAction("Down"))
sequence.append(KeyComboAction("Down"))
sequence.append(KeyComboAction("Down"))
sequence.append(KeyComboAction("Down"))
sequence.append(KeyComboAction("Left"))
sequence.append(KeyComboAction("space"))
sequence.append(PauseAction(3000))
sequence.append(KeyComboAction("Tab"))
sequence.append(PauseAction(3000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "3. Focus Hue color chooser",
    ["BRAILLE LINE:  'gtk3-demo application Changing color dialog Hue 0.00 color chooser'",
     "     VISIBLE:  'Hue 0.00 color chooser', cursor=1",
     "SPEECH OUTPUT: 'color chooser 0.00'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "4. Change Hue value",
    ["BRAILLE LINE:  'gtk3-demo application Changing color dialog Hue 0.01 color chooser'",
     "     VISIBLE:  'Hue 0.01 color chooser', cursor=1",
     "SPEECH OUTPUT: '0.01'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "5. Change Hue value",
    ["BRAILLE LINE:  'gtk3-demo application Changing color dialog Hue 0.02 color chooser'",
     "     VISIBLE:  'Hue 0.02 color chooser', cursor=1",
     "SPEECH OUTPUT: '0.02'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "6. Hue Where Am I",
    ["BRAILLE LINE:  'gtk3-demo application Changing color dialog Hue 0.02 color chooser'",
     "     VISIBLE:  'Hue 0.02 color chooser', cursor=1",
     "SPEECH OUTPUT: 'color chooser 0.02 2 percent.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "7. Focus Color Plane color chooser",
    ["BRAILLE LINE:  'gtk3-demo application Changing color dialog Color Plane color chooser'",
     "     VISIBLE:  'Color Plane color chooser', cursor=1",
     "SPEECH OUTPUT: 'color chooser'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "8. Change value in Plane",
    ["KNOWN ISSUE: We are presenting nothing here.",
     ""]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "9. Change value in Plane",
    ["KNOWN ISSUE: We are presenting nothing here.",
     ""]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "10. Plane Where Am I",
    ["KNOWN ISSUE: We're not presenting the value here.",
     "BRAILLE LINE:  'gtk3-demo application Changing color dialog Color Plane color chooser'",
     "     VISIBLE:  'Color Plane color chooser', cursor=1",
     "SPEECH OUTPUT: 'color chooser'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "11. Focus Alpha color chooser",
    ["BRAILLE LINE:  'gtk3-demo application Changing color dialog Alpha 1.00 color chooser'",
     "     VISIBLE:  'Alpha 1.00 color chooser', cursor=1",
     "SPEECH OUTPUT: 'color chooser 1.00'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "12. Change Alpha value",
     ["BRAILLE LINE:  'gtk3-demo application Changing color dialog Alpha 0.99 color chooser'",
      "     VISIBLE:  'Alpha 0.99 color chooser', cursor=1",
      "SPEECH OUTPUT: '0.99'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "13. Alpha Where Am I",
    ["BRAILLE LINE:  'gtk3-demo application Changing color dialog Alpha 0.99 color chooser'",
     "     VISIBLE:  'Alpha 0.99 color chooser', cursor=1",
     "SPEECH OUTPUT: 'color chooser 0.99 99 percent.'"]))

sequence.append(KeyComboAction("<Alt>F4"))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
