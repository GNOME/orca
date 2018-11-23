#!/usr/bin/python

"""Test of find result presentation."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

#sequence.append(WaitForDocLoad())
sequence.append(PauseAction(3000))
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(PauseAction(3000))
sequence.append(KeyComboAction("<Control>F"))
sequence.append(PauseAction(3000))
sequence.append(TypeAction("orca"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(utils.AssertPresentationAction(
    "1. Return to next result",
    ["BRAILLE LINE:  'Welcome to Orca! h1'",
     "     VISIBLE:  'Welcome to Orca! h1', cursor=16",
     "SPEECH OUTPUT: 'Welcome to Orca! heading level 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(utils.AssertPresentationAction(
    "2. Return to next result",
    ["BRAILLE LINE:  'Welcome to Orca!'",
     "     VISIBLE:  'Welcome to Orca!', cursor=1",
     "SPEECH OUTPUT: '1.'",
     "SPEECH OUTPUT: 'Welcome to Orca!'",
     "SPEECH OUTPUT: 'link.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(utils.AssertPresentationAction(
    "3. Return to next result",
    ["BRAILLE LINE:  'Orca is a free, open source, flexible, extensible, and '",
     "     VISIBLE:  'Orca is a free, open source, fle', cursor=5",
     "SPEECH OUTPUT: 'Orca is a free, open source, flexible, extensible, and'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(utils.AssertPresentationAction(
    "4. Return to next result",
    ["BRAILLE LINE:  'synthesis, braille, and magnification, Orca helps provide '",
     "     VISIBLE:  'magnification, Orca helps provid', cursor=20",
     "SPEECH OUTPUT: 'synthesis, braille, and magnification, Orca helps provide'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Escape"))
sequence.append(utils.AssertPresentationAction(
    "5. Escape to return to page content",
    ["BRAILLE LINE:  'synthesis, braille, and magnification, Orca helps provide '",
     "     VISIBLE:  'magnification, Orca helps provid', cursor=20",
     "SPEECH OUTPUT: 'synthesis, braille, and magnification, Orca helps provide  selected'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "6. Down arrow to be sure we've updated our position",
    ["BRAILLE LINE:  'access to applications and toolkits that support the AT-SPI'",
     "     VISIBLE:  'access to applications and toolk', cursor=1",
     "SPEECH OUTPUT: 'access to applications and toolkits that support the AT-SPI'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
