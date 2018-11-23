#!/usr/bin/python

"""Test of checkbox output."""

from macaroon.playback import *

sequence = MacroSequence()
import utils

sequence.append(KeyComboAction("<Control>f"))
sequence.append(TypeAction("Paned Widgets"))
sequence.append(KeyComboAction("Return"))
sequence.append(KeyComboAction("Return"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("<Shift>ISO_Left_Tab"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "1. Tab to first checkbox",
    ["BRAILLE LINE:  'gtk-demo application Panes frame Horizontal panel < > Resize check box'",
     "     VISIBLE:  '< > Resize check box', cursor=1",
     "SPEECH OUTPUT: 'Horizontal panel.'",
     "SPEECH OUTPUT: 'Resize check box not checked.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "2. Where Am I",
    ["BRAILLE LINE:  'gtk-demo application Panes frame Horizontal panel < > Resize check box'",
     "     VISIBLE:  '< > Resize check box', cursor=1",
     "SPEECH OUTPUT: 'Horizontal Resize check box not checked.'",
     "SPEECH OUTPUT: 'Alt+R'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction(" "))
sequence.append(utils.AssertPresentationAction(
    "3. Toggle its state",
    ["BRAILLE LINE:  'gtk-demo application Panes frame Horizontal panel <x> Resize check box'",
     "     VISIBLE:  '<x> Resize check box', cursor=1",
     "SPEECH OUTPUT: 'checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "4. Where Am I",
    ["BRAILLE LINE:  'gtk-demo application Panes frame Horizontal panel <x> Resize check box'",
     "     VISIBLE:  '<x> Resize check box', cursor=1",
     "SPEECH OUTPUT: 'Horizontal Resize check box checked.'",
     "SPEECH OUTPUT: 'Alt+R'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction(" "))
sequence.append(utils.AssertPresentationAction(
    "5. Toggle its state back",
    ["BRAILLE LINE:  'gtk-demo application Panes frame Horizontal panel < > Resize check box'",
     "     VISIBLE:  '< > Resize check box', cursor=1",
     "SPEECH OUTPUT: 'not checked'"]))

sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("Tab"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "6. Tab to first checkbox in next panel",
    ["BRAILLE LINE:  'gtk-demo application Panes frame Vertical panel < > Resize check box'",
     "     VISIBLE:  '< > Resize check box', cursor=1",
     "SPEECH OUTPUT: 'Vertical panel.'",
     "SPEECH OUTPUT: 'Resize check box not checked.'"]))

sequence.append(KeyComboAction("<Alt>F4"))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
