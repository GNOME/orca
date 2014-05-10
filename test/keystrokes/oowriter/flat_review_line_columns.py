#!/usr/bin/python

"""Test flat review in multi-columned text."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(PauseAction(1000))
sequence.append(KeyComboAction("<Control>Home"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_8"))
sequence.append(utils.AssertPresentationAction(
    "1. Review current line.",
    ["BRAILLE LINE:  'ruler EFFector Vol. 19, No. 38  October  Intercept Personal  $l'",
     "     VISIBLE:  'EFFector Vol. 19, No. 38  Octobe', cursor=1",
     "SPEECH OUTPUT: 'ruler EFFector Vol. 19, No. 38  October  Intercept Personal ",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_9"))
sequence.append(utils.AssertPresentationAction(
    "2. Review next line.",
    ["BRAILLE LINE:  '10, 2006  editor@eff.org Communications $l'",
     "     VISIBLE:  '10, 2006  editor@eff.org Communi', cursor=1",
     "SPEECH OUTPUT: '10, 2006  editor@eff.org",
     " Communications",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_9"))
sequence.append(utils.AssertPresentationAction(
    "3. Review next line.",
    ["BRAILLE LINE:  '  $l'",
     "     VISIBLE:  '  $l', cursor=1",
     "SPEECH OUTPUT: 'white space'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_9"))
sequence.append(utils.AssertPresentationAction(
    "4. Review next line.",
    ["BRAILLE LINE:  'A Publication of the Electronic  Washington, D.C. - The FLAG  $l'",
     "     VISIBLE:  'A Publication of the Electronic ', cursor=1",
     "SPEECH OUTPUT: 'A Publication of the Electronic  Washington, D.C. - The FLAG '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_7"))
sequence.append(utils.AssertPresentationAction(
    "5. Review previous line.",
    ["BRAILLE LINE:  '  $l'",
     "     VISIBLE:  '  $l', cursor=1",
     "SPEECH OUTPUT: 'white space'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_7"))
sequence.append(utils.AssertPresentationAction(
    "6. Review previous line.",
    ["BRAILLE LINE:  '10, 2006  editor@eff.org Communications $l'",
     "     VISIBLE:  '10, 2006  editor@eff.org Communi', cursor=1",
     "SPEECH OUTPUT: '10, 2006  editor@eff.org",
     " Communications",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_7"))
sequence.append(utils.AssertPresentationAction(
    "7. Review previous line.",
    ["BRAILLE LINE:  'ruler EFFector Vol. 19, No. 38  October  Intercept Personal  $l'",
     "     VISIBLE:  'ruler EFFector Vol. 19, No. 38  ', cursor=1",
     "SPEECH OUTPUT: 'ruler EFFector Vol. 19, No. 38  October  Intercept Personal ",
     "'"]))

sequence.append(KeyComboAction("<Control>w"))
sequence.append(utils.AssertionSummaryAction())
sequence.start()
