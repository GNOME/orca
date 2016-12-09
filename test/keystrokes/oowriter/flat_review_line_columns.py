#!/usr/bin/python

"""Test flat review in multi-columned text."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(PauseAction(3000))
sequence.append(KeyComboAction("<Alt>v"))
sequence.append(KeyComboAction("Down"))
sequence.append(KeyComboAction("Down"))
sequence.append(KeyComboAction("Down"))
sequence.append(KeyComboAction("Down"))
sequence.append(KeyComboAction("Down"))
sequence.append(KeyComboAction("Down"))
sequence.append(KeyComboAction("Down"))
sequence.append(KeyComboAction("Down"))
sequence.append(KeyComboAction("Down"))
sequence.append(KeyComboAction("Down"))
sequence.append(KeyComboAction("Down"))
sequence.append(KeyComboAction("Down"))
sequence.append(KeyComboAction("Down"))
sequence.append(KeyComboAction("Down"))
sequence.append(KeyComboAction("Down"))
sequence.append(PauseAction(3000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "1. Down to menu item",
    ["BRAILLE LINE:  'soffice application column-example.odt - LibreOffice Writer frame <x> Sidebar check menu item'",
     "     VISIBLE:  '<x> Sidebar check menu item', cursor=1",
     "SPEECH OUTPUT: 'Sidebar check menu item checked.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(utils.AssertPresentationAction(
    "2. Return on menu item",
    ["KNOWN ISSUE: We're not getting anything other than the window:activate event",
     "BRAILLE LINE:  'soffice application column-example.odt - LibreOffice Writer frame'",
     "     VISIBLE:  'column-example.odt - LibreOffice', cursor=1",
     "SPEECH OUTPUT: 'column-example.odt - LibreOffice Writer frame'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "3. Down in document",
    ["BRAILLE LINE:  '10, 2006  editor@eff.org $l'",
     "     VISIBLE:  '10, 2006  editor@eff.org $l', cursor=1",
     "SPEECH OUTPUT: '10, 2006  editor@eff.org link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "4. Top of file.",
    ["BRAILLE LINE:  'column-example.odt - LibreOffice Writer frame column-example.odt - LibreOffice Writer root pane column-example - LibreOffice Document EFFector Vol. 19, No. 38  October  $l'",
     "     VISIBLE:  'EFFector Vol. 19, No. 38  Octobe', cursor=1",
     "SPEECH OUTPUT: 'EFFector Vol. 19, No. 38  October '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_8"))
sequence.append(utils.AssertPresentationAction(
    "5. Review current line.",
    ["BRAILLE LINE:  'EFFector Vol. 19, No. 38  October  Intercept Personal  $l'",
     "     VISIBLE:  'EFFector Vol. 19, No. 38  Octobe', cursor=1",
     "SPEECH OUTPUT: 'EFFector Vol. 19, No. 38  October  Intercept Personal ",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_8"))
sequence.append(utils.AssertPresentationAction(
    "6. Review current line.",
    ["BRAILLE LINE:  'EFFector Vol. 19, No. 38  October  Intercept Personal  $l'",
     "     VISIBLE:  'EFFector Vol. 19, No. 38  Octobe', cursor=1",
     "SPEECH OUTPUT: 'EFFector Vol. 19, No. 38  October  Intercept Personal ",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_9"))
sequence.append(utils.AssertPresentationAction(
    "7. Review next line.",
    ["BRAILLE LINE:  '10, 2006  editor@eff.org Communications $l'",
     "     VISIBLE:  '10, 2006  editor@eff.org Communi', cursor=1",
     "SPEECH OUTPUT: '10, 2006  editor@eff.org",
     " Communications",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_9"))
sequence.append(utils.AssertPresentationAction(
    "8. Review next line.",
    ["BRAILLE LINE:  '  $l'",
     "     VISIBLE:  '  $l', cursor=1",
     "SPEECH OUTPUT: 'white space'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_9"))
sequence.append(utils.AssertPresentationAction(
    "9. Review next line.",
    ["BRAILLE LINE:  'A Publication of the Electronic  Washington, D.C. - The FLAG  $l'",
     "     VISIBLE:  'A Publication of the Electronic ', cursor=1",
     "SPEECH OUTPUT: 'A Publication of the Electronic  Washington, D.C. - The FLAG '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_7"))
sequence.append(utils.AssertPresentationAction(
    "10. Review previous line.",
    ["BRAILLE LINE:  '  $l'",
     "     VISIBLE:  '  $l', cursor=1",
     "SPEECH OUTPUT: 'white space'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_7"))
sequence.append(utils.AssertPresentationAction(
    "11. Review previous line.",
    ["BRAILLE LINE:  '10, 2006  editor@eff.org Communications $l'",
     "     VISIBLE:  '10, 2006  editor@eff.org Communi', cursor=1",
     "SPEECH OUTPUT: '10, 2006  editor@eff.org",
     " Communications",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_7"))
sequence.append(utils.AssertPresentationAction(
    "12. Review previous line.",
    ["BRAILLE LINE:  'EFFector Vol. 19, No. 38  October  Intercept Personal  $l'",
     "     VISIBLE:  'EFFector Vol. 19, No. 38  Octobe', cursor=1",
     "SPEECH OUTPUT: 'EFFector Vol. 19, No. 38  October  Intercept Personal ",
     "'"]))

sequence.append(KeyComboAction("<Alt>F4"))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
