#!/usr/bin/python

"""Test flat review on menubar."""

from macaroon.playback import *
import utils

sequence = MacroSequence()
sequence.append(PauseAction(3000))
sequence.append(KeyComboAction("F6"))
sequence.append(PauseAction(3000))
sequence.append(KeyComboAction("KP_8"))
sequence.append(PauseAction(3000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_7"))
sequence.append(utils.AssertPresentationAction(
    "1. Review previous line.",
    ["BRAILLE LINE:  'File Edit View Insert Format Styles Table Form Tools Window Help $l'",
     "     VISIBLE:  'File Edit View Insert Format Sty', cursor=1",
     "SPEECH OUTPUT: 'File Edit View Insert Format Styles Table Form Tools Window Help'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_5"))
sequence.append(utils.AssertPresentationAction(
    "2. Review current word.",
    ["BRAILLE LINE:  'File Edit View Insert Format Styles Table Form Tools Window Help $l'",
     "     VISIBLE:  'File Edit View Insert Format Sty', cursor=1",
     "SPEECH OUTPUT: 'File'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_6"))
sequence.append(utils.AssertPresentationAction(
    "3. Review next word.",
    ["BRAILLE LINE:  'File Edit View Insert Format Styles Table Form Tools Window Help $l'",
     "     VISIBLE:  'Edit View Insert Format Styles T', cursor=1",
     "SPEECH OUTPUT: 'Edit'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_6"))
sequence.append(utils.AssertPresentationAction(
    "4. Review next word.",
    ["BRAILLE LINE:  'File Edit View Insert Format Styles Table Form Tools Window Help $l'",
     "     VISIBLE:  'View Insert Format Styles Table ', cursor=1",
     "SPEECH OUTPUT: 'View'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_4"))
sequence.append(utils.AssertPresentationAction(
    "5. Review previous word.",
    ["BRAILLE LINE:  'File Edit View Insert Format Styles Table Form Tools Window Help $l'",
     "     VISIBLE:  'Edit View Insert Format Styles T', cursor=1",
     "SPEECH OUTPUT: 'Edit'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_4"))
sequence.append(utils.AssertPresentationAction(
    "6. Review previous word.",
    ["BRAILLE LINE:  'File Edit View Insert Format Styles Table Form Tools Window Help $l'",
     "     VISIBLE:  'File Edit View Insert Format Sty', cursor=1",
     "SPEECH OUTPUT: 'File'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_2"))
sequence.append(utils.AssertPresentationAction(
    "7. Review current char.",
    ["BRAILLE LINE:  'File Edit View Insert Format Styles Table Form Tools Window Help $l'",
     "     VISIBLE:  'File Edit View Insert Format Sty', cursor=1",
     "SPEECH OUTPUT: 'F'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_2"))
sequence.append(KeyComboAction("KP_2"))
sequence.append(utils.AssertPresentationAction(
    "8. Spell current char.",
    ["BRAILLE LINE:  'File Edit View Insert Format Styles Table Form Tools Window Help $l'",
     "     VISIBLE:  'File Edit View Insert Format Sty', cursor=1",
     "BRAILLE LINE:  'File Edit View Insert Format Styles Table Form Tools Window Help $l'",
     "     VISIBLE:  'File Edit View Insert Format Sty', cursor=1",
     "SPEECH OUTPUT: 'F'",
     "SPEECH OUTPUT: 'foxtrot'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_2"))
sequence.append(KeyComboAction("KP_2"))
sequence.append(KeyComboAction("KP_2"))
sequence.append(utils.AssertPresentationAction(
    "9. Unicode for current char.",
    ["BRAILLE LINE:  'File Edit View Insert Format Styles Table Form Tools Window Help $l'",
     "     VISIBLE:  'File Edit View Insert Format Sty', cursor=1",
     "BRAILLE LINE:  'File Edit View Insert Format Styles Table Form Tools Window Help $l'",
     "     VISIBLE:  'File Edit View Insert Format Sty', cursor=1",
     "BRAILLE LINE:  'File Edit View Insert Format Styles Table Form Tools Window Help $l'",
     "     VISIBLE:  'File Edit View Insert Format Sty', cursor=1",
     "SPEECH OUTPUT: 'F'",
     "SPEECH OUTPUT: 'foxtrot'",
     "SPEECH OUTPUT: 'Unicode 0046'"]))

sequence.append(KeyComboAction("<Alt>F4"))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
