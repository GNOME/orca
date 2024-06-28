#!/usr/bin/python

"""Test of column header output."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(KeyComboAction("End"))
sequence.append(KeyComboAction("Up"))
sequence.append(KeyComboAction("<Shift>Right"))
sequence.append(KeyComboAction("Down"))
sequence.append(KeyComboAction("Down"))
sequence.append(KeyComboAction("Return"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>ISO_Left_Tab"))
sequence.append(utils.AssertPresentationAction(
    "1. Bug number column header",
    ["BRAILLE LINE:  'gtk-demo application GtkListStore demo frame table Bug number table column header'",
     "     VISIBLE:  'Bug number table column header', cursor=1",
     "SPEECH OUTPUT: 'Bug number table column header not selected'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "2. Severity column header",
    ["BRAILLE LINE:  'gtk-demo application GtkListStore demo frame table Severity table column header'",
     "     VISIBLE:  'Severity table column header', cursor=1",
     "SPEECH OUTPUT: 'Severity table column header'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "3. Description column header",
    ["BRAILLE LINE:  'gtk-demo application GtkListStore demo frame table Description table column header'",
     "     VISIBLE:  'Description table column header', cursor=1",
     "SPEECH OUTPUT: 'Description table column header'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "4. Enter table",
    ["BRAILLE LINE:  'gtk-demo application GtkListStore demo frame table Description column header < > Fixed? 60482 Normal scrollable notebooks and hidden tabs '",
     "     VISIBLE:  'scrollable notebooks and hidden ', cursor=1",
     "BRAILLE LINE:  'gtk-demo application GtkListStore demo frame table Fixed? column header < > Fixed? 60482 Normal scrollable notebooks and hidden tabs '",
     "     VISIBLE:  '< > Fixed? 60482 Normal scrollab', cursor=1",
     "SPEECH OUTPUT: 'Fixed?'",
     "SPEECH OUTPUT: 'check box not checked.'",
     "SPEECH OUTPUT: '60482.'",
     "SPEECH OUTPUT: 'Normal.'",
     "SPEECH OUTPUT: 'scrollable notebooks and hidden tabs.'",
     "SPEECH OUTPUT: 'Fixed? column header check box not checked.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "5. Normal cell",
    ["BRAILLE LINE:  'gtk-demo application GtkListStore demo frame table Severity column header < > Fixed? 60482 Normal scrollable notebooks and hidden tabs '",
     "     VISIBLE:  'Normal scrollable notebooks and ', cursor=1",
     "SPEECH OUTPUT: 'Severity column header Normal.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "6. Normal cell basic Where Am I",
    ["BRAILLE LINE:  'gtk-demo application GtkListStore demo frame table Severity column header < > Fixed? 60482 Normal scrollable notebooks and hidden tabs '",
     "     VISIBLE:  'Normal scrollable notebooks and ', cursor=1",
     "SPEECH OUTPUT: 'table.'",
     "SPEECH OUTPUT: 'Severity.'",
     "SPEECH OUTPUT: 'table cell.'",
     "SPEECH OUTPUT: 'Normal.'",
     "SPEECH OUTPUT: 'column 3 of 5'",
     "SPEECH OUTPUT: 'row 1 of 14.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "7. Normal cell detailed Where Am I",
    ["BRAILLE LINE:  'gtk-demo application GtkListStore demo frame table Severity column header < > Fixed? 60482 Normal scrollable notebooks and hidden tabs '",
     "     VISIBLE:  'Normal scrollable notebooks and ', cursor=1",
     "BRAILLE LINE:  'gtk-demo application GtkListStore demo frame table Severity column header < > Fixed? 60482 Normal scrollable notebooks and hidden tabs '",
     "     VISIBLE:  'Normal scrollable notebooks and ', cursor=1",
     "SPEECH OUTPUT: 'table.'",
     "SPEECH OUTPUT: 'Severity.'",
     "SPEECH OUTPUT: 'table cell.'",
     "SPEECH OUTPUT: 'Normal.'",
     "SPEECH OUTPUT: 'column 3 of 5'",
     "SPEECH OUTPUT: 'row 1 of 14.'",
     "SPEECH OUTPUT: 'table.'",
     "SPEECH OUTPUT: 'Severity.'",
     "SPEECH OUTPUT: 'table cell.'",
     "SPEECH OUTPUT: 'Normal.'",
     "SPEECH OUTPUT: 'column 3 of 5'",
     "SPEECH OUTPUT: 'row 1 of 14.'",
     "SPEECH OUTPUT: 'Fixed?'",
     "SPEECH OUTPUT: 'check box not checked.'",
     "SPEECH OUTPUT: '60482.'",
     "SPEECH OUTPUT: 'Normal.'",
     "SPEECH OUTPUT: 'scrollable notebooks and hidden tabs.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "8. 60482 cell",
    ["BRAILLE LINE:  'gtk-demo application GtkListStore demo frame table Bug number column header < > Fixed? 60482 Normal scrollable notebooks and hidden tabs '",
     "     VISIBLE:  '60482 Normal scrollable notebook', cursor=1",
     "SPEECH OUTPUT: 'Bug number column header 60482.'"]))

sequence.append(KeyComboAction("<Alt>F4"))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
