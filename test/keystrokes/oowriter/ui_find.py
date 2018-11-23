#!/usr/bin/python

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(PauseAction(3000))
sequence.append(KeyComboAction("<Control>Home"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>f"))
sequence.append(utils.AssertPresentationAction(
    "1. Ctrl+F",
    ["KNOWN ISSUE: We're double-presenting the combobox name",
     "BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Writer root pane Find tool bar  $l combo box'",
     "     VISIBLE:  'Find tool bar  $l combo box', cursor=15",
     "SPEECH OUTPUT: 'Find tool bar'",
     "SPEECH OUTPUT: 'Find Text Find Text editable combo box.'"]))

sequence.append(TypeAction("foo"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "2. Tab",
    ["BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Writer root pane Find tool bar  $l combo box'",
     "     VISIBLE:  'Find Previous push button', cursor=1",
     "SPEECH OUTPUT: 'Find Previous push button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>ISO_Left_Tab"))
sequence.append(utils.AssertPresentationAction(
    "3. Shift+Tab",
    ["BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Writer root pane Find tool bar Find Previous push button'",
     "     VISIBLE:  'foo $l combo box', cursor=4",
     "SPEECH OUTPUT: 'Find Text Find Text editable combo box.'",
     "SPEECH OUTPUT: 'foo selected'"]))

sequence.append(KeyComboAction("<Alt>F4"))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
