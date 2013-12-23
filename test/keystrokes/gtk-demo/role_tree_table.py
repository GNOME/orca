#!/usr/bin/python

"""Test of tree table output."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(KeyComboAction("End"))
sequence.append(KeyComboAction("<Shift>Right"))
sequence.append(KeyComboAction("Down"))
sequence.append(KeyComboAction("Down"))
sequence.append(KeyComboAction("Down"))
sequence.append(KeyComboAction("Return"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "January cell focus",
    ["BRAILLE LINE:  'gtk-demo application Card planning sheet frame tree table Holiday column header January expanded < > Alex < > Havoc < > Tim < > Owen < > Dave TREE LEVEL 1'",
     "     VISIBLE:  'January expanded < > Alex < > Ha', cursor=1",
     "SPEECH OUTPUT: 'tree table'",
     "SPEECH OUTPUT: 'Holiday column header January expanded 3 items Alex check box not checked Havoc check box not checked Tim check box not checked Owen check box not checked Dave check box not checked tree level 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "January cell basic Where Am I",
    ["BRAILLE LINE:  'gtk-demo application Card planning sheet frame tree table Holiday column header January expanded < > Alex < > Havoc < > Tim < > Owen < > Dave TREE LEVEL 1'",
     "     VISIBLE:  'January expanded < > Alex < > Ha', cursor=1",
     "SPEECH OUTPUT: 'tree table Holiday table cell January column 1 of 6 row 1 of 53 expanded tree level 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "January cell detailed Where Am I",
    ["BRAILLE LINE:  'gtk-demo application Card planning sheet frame tree table Holiday column header January expanded < > Alex < > Havoc < > Tim < > Owen < > Dave TREE LEVEL 1'",
     "     VISIBLE:  'January expanded < > Alex < > Ha', cursor=1",
     "BRAILLE LINE:  'gtk-demo application Card planning sheet frame tree table Holiday column header January expanded < > Alex < > Havoc < > Tim < > Owen < > Dave TREE LEVEL 1'",
     "     VISIBLE:  'January expanded < > Alex < > Ha', cursor=1",
     "SPEECH OUTPUT: 'tree table Holiday table cell January column 1 of 6 row 1 of 53 expanded tree level 1'",
     "SPEECH OUTPUT: 'tree table Holiday table cell January column 1 of 6 row 1 of 53 January expanded 3 items Alex check box not checked Havoc check box not checked Tim check box not checked Owen check box not checked Dave check box not checked expanded tree level 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>Left"))
sequence.append(utils.AssertPresentationAction(
    "January cell collapsed",
    ["BRAILLE LINE:  'gtk-demo application Card planning sheet frame tree table Holiday column header January collapsed < > Alex < > Havoc < > Tim < > Owen < > Dave TREE LEVEL 1'",
     "     VISIBLE:  'January collapsed < > Alex < > H', cursor=1",
     "SPEECH OUTPUT: 'collapsed'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "January cell collapsed basic Where Am I",
    ["BRAILLE LINE:  'gtk-demo application Card planning sheet frame tree table Holiday column header January collapsed < > Alex < > Havoc < > Tim < > Owen < > Dave TREE LEVEL 1'",
     "     VISIBLE:  'January collapsed < > Alex < > H', cursor=1",
     "SPEECH OUTPUT: 'tree table Holiday table cell January column 1 of 6 row 1 of 50 collapsed tree level 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "January cell collapsed detailed Where Am I",
    ["BRAILLE LINE:  'gtk-demo application Card planning sheet frame tree table Holiday column header January collapsed < > Alex < > Havoc < > Tim < > Owen < > Dave TREE LEVEL 1'",
     "     VISIBLE:  'January collapsed < > Alex < > H', cursor=1",
     "BRAILLE LINE:  'gtk-demo application Card planning sheet frame tree table Holiday column header January collapsed < > Alex < > Havoc < > Tim < > Owen < > Dave TREE LEVEL 1'",
     "     VISIBLE:  'January collapsed < > Alex < > H', cursor=1",
     "SPEECH OUTPUT: 'tree table Holiday table cell January column 1 of 6 row 1 of 50 collapsed tree level 1'",
     "SPEECH OUTPUT: 'tree table Holiday table cell January column 1 of 6 row 1 of 50 January collapsed Alex check box not checked Havoc check box not checked Tim check box not checked Owen check box not checked Dave check box not checked collapsed tree level 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>Right"))
sequence.append(utils.AssertPresentationAction(
    "January cell expanded",
   ["BRAILLE LINE:  'gtk-demo application Card planning sheet frame tree table Holiday column header January expanded < > Alex < > Havoc < > Tim < > Owen < > Dave TREE LEVEL 1'",
    "     VISIBLE:  'January expanded < > Alex < > Ha', cursor=1",
    "SPEECH OUTPUT: 'expanded 2 items'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "New Year's Day cell",
    ["BRAILLE LINE:  'gtk-demo application Card planning sheet frame tree table Holiday column header New Years Day <x> Alex <x> Havoc <x> Tim <x> Owen < > Dave TREE LEVEL 2'",
     "     VISIBLE:  'New Years Day <x> Alex <x> Havoc', cursor=1",
     "SPEECH OUTPUT: 'New Years Day Alex check box checked Havoc check box checked Tim check box checked Owen check box checked Dave check box not checked tree level 2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "Alex checkbox cell",
    ["BRAILLE LINE:  'gtk-demo application Card planning sheet frame tree table Alex column header New Years Day <x> Alex <x> Havoc <x> Tim <x> Owen < > Dave'",
     "     VISIBLE:  '<x> Alex <x> Havoc <x> Tim <x> O', cursor=1",
     "SPEECH OUTPUT: 'Alex column header check box checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "Alex checkbox cell basic Where Am I",
    ["BRAILLE LINE:  'gtk-demo application Card planning sheet frame tree table Alex column header New Years Day <x> Alex <x> Havoc <x> Tim <x> Owen < > Dave'",
     "     VISIBLE:  '<x> Alex <x> Havoc <x> Tim <x> O', cursor=1",
     "SPEECH OUTPUT: 'tree table Alex table cell check box checked column 2 of 6 row 2 of 53'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "Alex checkbox cell detailed Where Am I",
    ["BRAILLE LINE:  'gtk-demo application Card planning sheet frame tree table Alex column header New Years Day <x> Alex <x> Havoc <x> Tim <x> Owen < > Dave'",
     "     VISIBLE:  '<x> Alex <x> Havoc <x> Tim <x> O', cursor=1",
     "BRAILLE LINE:  'gtk-demo application Card planning sheet frame tree table Alex column header New Years Day <x> Alex <x> Havoc <x> Tim <x> Owen < > Dave'",
     "     VISIBLE:  '<x> Alex <x> Havoc <x> Tim <x> O', cursor=1",
     "SPEECH OUTPUT: 'tree table Alex table cell check box checked column 2 of 6 row 2 of 53'",
     "SPEECH OUTPUT: 'tree table Alex table cell check box checked column 2 of 6 row 2 of 53 New Years Day Alex check box checked Havoc check box checked Tim check box checked Owen check box checked Dave check box not checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction(" "))
sequence.append(utils.AssertPresentationAction(
    "Alex checkbox cell unchecked",
    ["BRAILLE LINE:  'gtk-demo application Card planning sheet frame tree table Alex column header New Years Day < > Alex <x> Havoc <x> Tim <x> Owen < > Dave'",
     "     VISIBLE:  '< > Alex <x> Havoc <x> Tim <x> O', cursor=1",
     "SPEECH OUTPUT: 'not checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction(" "))
sequence.append(utils.AssertPresentationAction(
    "Alex checkbox cell checked",
    ["BRAILLE LINE:  'gtk-demo application Card planning sheet frame tree table Alex column header New Years Day <x> Alex <x> Havoc <x> Tim <x> Owen < > Dave'",
     "     VISIBLE:  '<x> Alex <x> Havoc <x> Tim <x> O', cursor=1",
     "SPEECH OUTPUT: 'checked'"]))

sequence.append(KeyComboAction("<Alt>F4"))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
