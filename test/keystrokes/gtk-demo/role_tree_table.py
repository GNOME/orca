#!/usr/bin/python

"""Test of tree table output."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(KeyComboAction("End"))
sequence.append(KeyComboAction("Up"))
sequence.append(KeyComboAction("<Shift>Right"))
sequence.append(KeyComboAction("Down"))
sequence.append(KeyComboAction("Down"))
sequence.append(KeyComboAction("Down"))
sequence.append(KeyComboAction("Return"))

sequence.append(KeyComboAction("Down"))
sequence.append(KeyComboAction("Down"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "1. January cell focus",
    ["BRAILLE LINE:  'gtk-demo application Card planning sheet frame tree table Holiday column header January expanded < > Alex < > Havoc < > Tim < > Owen < > Dave TREE LEVEL 1'",
     "     VISIBLE:  'January expanded < > Alex < > Ha', cursor=1",
     "SPEECH OUTPUT: 'January expanded 3 items.'",
     "SPEECH OUTPUT: 'Alex'",
     "SPEECH OUTPUT: 'check box not checked.'",
     "SPEECH OUTPUT: 'Havoc'",
     "SPEECH OUTPUT: 'check box not checked.'",
     "SPEECH OUTPUT: 'Tim'",
     "SPEECH OUTPUT: 'check box not checked.'",
     "SPEECH OUTPUT: 'Owen'",
     "SPEECH OUTPUT: 'check box not checked.'",
     "SPEECH OUTPUT: 'Dave'",
     "SPEECH OUTPUT: 'check box not checked.'",
     "SPEECH OUTPUT: 'tree level 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "2. January cell basic Where Am I",
    ["BRAILLE LINE:  'gtk-demo application Card planning sheet frame tree table Holiday column header January expanded < > Alex < > Havoc < > Tim < > Owen < > Dave TREE LEVEL 1'",
     "     VISIBLE:  'January expanded < > Alex < > Ha', cursor=1",
     "SPEECH OUTPUT: 'tree table.'",
     "SPEECH OUTPUT: 'Holiday.'",
     "SPEECH OUTPUT: 'table cell.'",
     "SPEECH OUTPUT: 'January.'",
     "SPEECH OUTPUT: 'column 1 of 6'",
     "SPEECH OUTPUT: 'row 1 of 53.'",
     "SPEECH OUTPUT: 'expanded.'",
     "SPEECH OUTPUT: 'tree level 1.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "3. January cell detailed Where Am I",
    ["BRAILLE LINE:  'gtk-demo application Card planning sheet frame tree table Holiday column header January expanded < > Alex < > Havoc < > Tim < > Owen < > Dave TREE LEVEL 1'",
     "     VISIBLE:  'January expanded < > Alex < > Ha', cursor=1",
     "BRAILLE LINE:  'gtk-demo application Card planning sheet frame tree table Holiday column header January expanded < > Alex < > Havoc < > Tim < > Owen < > Dave TREE LEVEL 1'",
     "     VISIBLE:  'January expanded < > Alex < > Ha', cursor=1",
     "SPEECH OUTPUT: 'tree table.'",
     "SPEECH OUTPUT: 'Holiday.'",
     "SPEECH OUTPUT: 'table cell.'",
     "SPEECH OUTPUT: 'January.'",
     "SPEECH OUTPUT: 'column 1 of 6'",
     "SPEECH OUTPUT: 'row 1 of 53.'",
     "SPEECH OUTPUT: 'expanded.'",
     "SPEECH OUTPUT: 'tree level 1.'",
     "SPEECH OUTPUT: 'tree table.'",
     "SPEECH OUTPUT: 'Holiday.'",
     "SPEECH OUTPUT: 'table cell.'",
     "SPEECH OUTPUT: 'January.'",
     "SPEECH OUTPUT: 'column 1 of 6'",
     "SPEECH OUTPUT: 'row 1 of 53.'",
     "SPEECH OUTPUT: 'January expanded 3 items.'",
     "SPEECH OUTPUT: 'Alex'",
     "SPEECH OUTPUT: 'check box not checked.'",
     "SPEECH OUTPUT: 'Havoc'",
     "SPEECH OUTPUT: 'check box not checked.'",
     "SPEECH OUTPUT: 'Tim'",
     "SPEECH OUTPUT: 'check box not checked.'",
     "SPEECH OUTPUT: 'Owen'",
     "SPEECH OUTPUT: 'check box not checked.'",
     "SPEECH OUTPUT: 'Dave'",
     "SPEECH OUTPUT: 'check box not checked.'",
     "SPEECH OUTPUT: 'expanded.'",
     "SPEECH OUTPUT: 'tree level 1.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>Left"))
sequence.append(utils.AssertPresentationAction(
    "4. January cell collapsed",
    ["BRAILLE LINE:  'gtk-demo application Card planning sheet frame tree table Holiday column header January collapsed < > Alex < > Havoc < > Tim < > Owen < > Dave TREE LEVEL 1'",
     "     VISIBLE:  'January collapsed < > Alex < > H', cursor=1",
     "SPEECH OUTPUT: 'collapsed.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "5. January cell collapsed basic Where Am I",
    ["BRAILLE LINE:  'gtk-demo application Card planning sheet frame tree table Holiday column header January collapsed < > Alex < > Havoc < > Tim < > Owen < > Dave TREE LEVEL 1'",
     "     VISIBLE:  'January collapsed < > Alex < > H', cursor=1",
     "SPEECH OUTPUT: 'tree table.'",
     "SPEECH OUTPUT: 'Holiday.'",
     "SPEECH OUTPUT: 'table cell.'",
     "SPEECH OUTPUT: 'January.'",
     "SPEECH OUTPUT: 'column 1 of 6'",
     "SPEECH OUTPUT: 'row 1 of 50.'",
     "SPEECH OUTPUT: 'collapsed.'",
     "SPEECH OUTPUT: 'tree level 1.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "6. January cell collapsed detailed Where Am I",
    ["BRAILLE LINE:  'gtk-demo application Card planning sheet frame tree table Holiday column header January collapsed < > Alex < > Havoc < > Tim < > Owen < > Dave TREE LEVEL 1'",
     "     VISIBLE:  'January collapsed < > Alex < > H', cursor=1",
     "BRAILLE LINE:  'gtk-demo application Card planning sheet frame tree table Holiday column header January collapsed < > Alex < > Havoc < > Tim < > Owen < > Dave TREE LEVEL 1'",
     "     VISIBLE:  'January collapsed < > Alex < > H', cursor=1",
     "SPEECH OUTPUT: 'tree table.'",
     "SPEECH OUTPUT: 'Holiday.'",
     "SPEECH OUTPUT: 'table cell.'",
     "SPEECH OUTPUT: 'January.'",
     "SPEECH OUTPUT: 'column 1 of 6'",
     "SPEECH OUTPUT: 'row 1 of 50.'",
     "SPEECH OUTPUT: 'collapsed.'",
     "SPEECH OUTPUT: 'tree level 1.'",
     "SPEECH OUTPUT: 'tree table.'",
     "SPEECH OUTPUT: 'Holiday.'",
     "SPEECH OUTPUT: 'table cell.'",
     "SPEECH OUTPUT: 'January.'",
     "SPEECH OUTPUT: 'column 1 of 6'",
     "SPEECH OUTPUT: 'row 1 of 50.'",
     "SPEECH OUTPUT: 'January collapsed.'",
     "SPEECH OUTPUT: 'Alex'",
     "SPEECH OUTPUT: 'check box not checked.'",
     "SPEECH OUTPUT: 'Havoc'",
     "SPEECH OUTPUT: 'check box not checked.'",
     "SPEECH OUTPUT: 'Tim'",
     "SPEECH OUTPUT: 'check box not checked.'",
     "SPEECH OUTPUT: 'Owen'",
     "SPEECH OUTPUT: 'check box not checked.'",
     "SPEECH OUTPUT: 'Dave'",
     "SPEECH OUTPUT: 'check box not checked.'",
     "SPEECH OUTPUT: 'collapsed.'",
     "SPEECH OUTPUT: 'tree level 1.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>Right"))
sequence.append(utils.AssertPresentationAction(
    "7. January cell expanded",
    ["BRAILLE LINE:  'gtk-demo application Card planning sheet frame tree table Holiday column header January expanded < > Alex < > Havoc < > Tim < > Owen < > Dave TREE LEVEL 1'",
    "     VISIBLE:  'January expanded < > Alex < > Ha', cursor=1",
     "SPEECH OUTPUT: 'expanded.'",
     "SPEECH OUTPUT: '3 items.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "8. New Year's Day cell",
    ["BRAILLE LINE:  'gtk-demo application Card planning sheet frame tree table Holiday column header New Years Day <x> Alex <x> Havoc <x> Tim <x> Owen < > Dave TREE LEVEL 2'",
     "     VISIBLE:  'New Years Day <x> Alex <x> Havoc', cursor=1",
     "SPEECH OUTPUT: 'New Years Day.'",
     "SPEECH OUTPUT: 'Alex'",
     "SPEECH OUTPUT: 'check box checked.'",
     "SPEECH OUTPUT: 'Havoc'",
     "SPEECH OUTPUT: 'check box checked.'",
     "SPEECH OUTPUT: 'Tim'",
     "SPEECH OUTPUT: 'check box checked.'",
     "SPEECH OUTPUT: 'Owen'",
     "SPEECH OUTPUT: 'check box checked.'",
     "SPEECH OUTPUT: 'Dave'",
     "SPEECH OUTPUT: 'check box not checked.'",
     "SPEECH OUTPUT: 'tree level 2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "9. Alex checkbox cell",
    ["BRAILLE LINE:  'gtk-demo application Card planning sheet frame tree table Alex column header New Years Day <x> Alex <x> Havoc <x> Tim <x> Owen < > Dave'",
     "     VISIBLE:  '<x> Alex <x> Havoc <x> Tim <x> O', cursor=1",
     "SPEECH OUTPUT: 'Alex column header check box checked.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "10. Alex checkbox cell basic Where Am I",
    ["BRAILLE LINE:  'gtk-demo application Card planning sheet frame tree table Alex column header New Years Day <x> Alex <x> Havoc <x> Tim <x> Owen < > Dave'",
     "     VISIBLE:  '<x> Alex <x> Havoc <x> Tim <x> O', cursor=1",
     "SPEECH OUTPUT: 'tree table.'",
     "SPEECH OUTPUT: 'Alex.'",
     "SPEECH OUTPUT: 'table cell.'",
     "SPEECH OUTPUT: 'check box checked.'",
     "SPEECH OUTPUT: 'column 2 of 6'",
     "SPEECH OUTPUT: 'row 2 of 53.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "11. Alex checkbox cell detailed Where Am I",
    ["BRAILLE LINE:  'gtk-demo application Card planning sheet frame tree table Alex column header New Years Day <x> Alex <x> Havoc <x> Tim <x> Owen < > Dave'",
     "     VISIBLE:  '<x> Alex <x> Havoc <x> Tim <x> O', cursor=1",
     "BRAILLE LINE:  'gtk-demo application Card planning sheet frame tree table Alex column header New Years Day <x> Alex <x> Havoc <x> Tim <x> Owen < > Dave'",
     "     VISIBLE:  '<x> Alex <x> Havoc <x> Tim <x> O', cursor=1",
     "SPEECH OUTPUT: 'tree table.'",
     "SPEECH OUTPUT: 'Alex.'",
     "SPEECH OUTPUT: 'table cell.'",
     "SPEECH OUTPUT: 'check box checked.'",
     "SPEECH OUTPUT: 'column 2 of 6'",
     "SPEECH OUTPUT: 'row 2 of 53.'",
     "SPEECH OUTPUT: 'tree table.'",
     "SPEECH OUTPUT: 'Alex.'",
     "SPEECH OUTPUT: 'table cell.'",
     "SPEECH OUTPUT: 'check box checked.'",
     "SPEECH OUTPUT: 'column 2 of 6'",
     "SPEECH OUTPUT: 'row 2 of 53.'",
     "SPEECH OUTPUT: 'New Years Day.'",
     "SPEECH OUTPUT: 'Alex'",
     "SPEECH OUTPUT: 'check box checked.'",
     "SPEECH OUTPUT: 'Havoc'",
     "SPEECH OUTPUT: 'check box checked.'",
     "SPEECH OUTPUT: 'Tim'",
     "SPEECH OUTPUT: 'check box checked.'",
     "SPEECH OUTPUT: 'Owen'",
     "SPEECH OUTPUT: 'check box checked.'",
     "SPEECH OUTPUT: 'Dave'",
     "SPEECH OUTPUT: 'check box not checked.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction(" "))
sequence.append(utils.AssertPresentationAction(
    "12. Alex checkbox cell unchecked",
    ["BRAILLE LINE:  'gtk-demo application Card planning sheet frame tree table Alex column header New Years Day < > Alex <x> Havoc <x> Tim <x> Owen < > Dave'",
     "     VISIBLE:  '< > Alex <x> Havoc <x> Tim <x> O', cursor=1",
     "SPEECH OUTPUT: 'not checked.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction(" "))
sequence.append(utils.AssertPresentationAction(
    "13. Alex checkbox cell checked",
    ["BRAILLE LINE:  'gtk-demo application Card planning sheet frame tree table Alex column header New Years Day <x> Alex <x> Havoc <x> Tim <x> Owen < > Dave'",
     "     VISIBLE:  '<x> Alex <x> Havoc <x> Tim <x> O', cursor=1",
     "SPEECH OUTPUT: 'checked.'"]))

sequence.append(KeyComboAction("<Alt>F4"))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
