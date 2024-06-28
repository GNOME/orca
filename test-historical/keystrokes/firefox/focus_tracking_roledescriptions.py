#!/usr/bin/python

from macaroon.playback import *
import utils

sequence = MacroSequence()

#sequence.append(WaitForDocLoad())
sequence.append(PauseAction(5000))
sequence.append(KeyComboAction("<Control>Home"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "1. Tab to a div with no roledescription",
    ["BRAILLE LINE:  'Focus me 1'",
     "     VISIBLE:  'Focus me 1', cursor=1",
     "SPEECH OUTPUT: 'Focus me 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "2. Tab to a div with only a roledescription",
    ["BRAILLE LINE:  'Focus me 2 kill switch'",
     "     VISIBLE:  'Focus me 2 kill switch', cursor=1",
     "SPEECH OUTPUT: 'Focus me 2 kill switch'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "3. Tab to a div with role button",
    ["BRAILLE LINE:  'Focus me 3 push button'",
     "     VISIBLE:  'Focus me 3 push button', cursor=1",
     "SPEECH OUTPUT: 'Focus me 3 push button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "4. Tab to a div with role button and a roledescription",
    ["BRAILLE LINE:  'Focus me 4 kill switch'",
     "     VISIBLE:  'Focus me 4 kill switch', cursor=1",
     "SPEECH OUTPUT: 'Focus me 4 kill switch'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "5. Tab to a button element",
    ["BRAILLE LINE:  'Focus me 5 push button'",
     "     VISIBLE:  'Focus me 5 push button', cursor=1",
     "SPEECH OUTPUT: 'Focus me 5 push button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "6. Tab to a button element with a roledescription",
    ["BRAILLE LINE:  'Focus me 6 kill switch'",
     "     VISIBLE:  'Focus me 6 kill switch', cursor=1",
     "SPEECH OUTPUT: 'Focus me 6 kill switch'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "7. Tab to a div with role group, a roledescription, a label, and displayed text",
    ["BRAILLE LINE:  'Presentation slide set'",
     "     VISIBLE:  'Presentation slide set', cursor=1",
     "BRAILLE LINE:  'Here are some slides'",
     "     VISIBLE:  'Here are some slides', cursor=1",
     "SPEECH OUTPUT: 'Presentation slide set.'",
     "SPEECH OUTPUT: 'Here are some slides'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "8. Tab to a div with role region, a roledescription, a labelledby, and displayed text",
    ["BRAILLE LINE:  'First Quarter 2015 slide'",
     "     VISIBLE:  'First Quarter 2015 slide', cursor=1",
     "BRAILLE LINE:  'First Quarter 2015 h1'",
     "     VISIBLE:  'First Quarter 2015 h1', cursor=1",
     "SPEECH OUTPUT: 'First Quarter 2015 slide.'",
     "SPEECH OUTPUT: 'First Quarter 2015 heading level 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "9. Tab to a div with a roledescription, a labelledby, and displayed text",
    ["BRAILLE LINE:  'Second Quarter 2015 slide'",
     "     VISIBLE:  'Second Quarter 2015 slide', cursor=1",
     "BRAILLE LINE:  'Second Quarter 2015 h1'",
     "     VISIBLE:  'Second Quarter 2015 h1', cursor=1",
     "SPEECH OUTPUT: 'leaving region.'",
     "SPEECH OUTPUT: 'Second Quarter 2015 slide'",
     "SPEECH OUTPUT: 'Second Quarter 2015 heading level 1'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
